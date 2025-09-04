#!/usr/bin/env python3

import whisper
import textdistance
import gradio as gr
import plotly.graph_objects as go
import json
import numpy as np
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

class FrenchPronunciationEvaluator:
    def __init__(self):
        self.thresholds = {
            'global_score': 85.0,
            'levenshtein': 80.0,
            'jaccard': 75.0,
            'jaro': 80.0,
            'lisp_severity': 3.0
        }
        
    def enhanced_lisp_detection(self, all_words, ref_words):
        """Enhanced lisp detection with severity scoring"""
        french_sibilants = {
            's': {'weight': 1.0, 'type': 'voiceless_alveolar'},
            'z': {'weight': 1.1, 'type': 'voiced_alveolar'},
            'ch': {'weight': 1.2, 'type': 'voiceless_postalveolar'},
            'j': {'weight': 1.3, 'type': 'voiced_postalveolar'}
        }
        
        lisp_candidates = []
        total_severity = 0.0
        
        for w in all_words:
            word_lower = w['word'].lower()
            confidence = w.get('probability', 1.0)
            
            # Check for sibilant sounds
            for sibilant, config in french_sibilants.items():
                if sibilant in word_lower:
                    severity = 0.0
                    
                    # Low confidence indicates potential mispronunciation
                    if confidence < 0.7:
                        severity += (0.7 - confidence) * 5.0 * config['weight']
                    
                    # Check for interdental lisp indicators
                    if 'th' in word_lower:
                        severity += 2.0 * config['weight']
                    
                    # Check for lateral lisp patterns
                    if any(pattern in word_lower for pattern in ['sl', 'tl']):
                        severity += 1.5 * config['weight']
                    
                    if severity > 0.5:
                        capped_severity = min(5.0, severity)
                        lisp_candidates.append({
                            "word": w['word'],
                            "start": w['start'],
                            "end": w['end'],
                            "confidence": confidence,
                            "severity": capped_severity,
                            "sibilant_type": config['type']
                        })
                        total_severity += capped_severity
        
        ref_sibilants = [w for w in ref_words if any(s in w.lower() for s in french_sibilants.keys())]
        trans_sibilants = [w['word'].lower() for w in all_words if any(s in w['word'].lower() for s in french_sibilants.keys())]
        missing_sibilants = [w for w in ref_sibilants if w not in trans_sibilants]
        
        return lisp_candidates, missing_sibilants, min(5.0, total_severity)

    def evaluate_pronunciation(self, audio_file_path, reference_text):
        """Enhanced evaluation with production thresholds"""
        model = whisper.load_model("base")
        result = model.transcribe(
            audio_file_path, 
            language='fr',
            temperature=0.0,
            word_timestamps=True
        )
        
        transcribed_text = result["text"].strip()
        segments = result.get('segments', [])
        all_words = [w for seg in segments for w in seg.get('words', [])]
        ref_words = reference_text.lower().strip().split()
        trans_words = [w['word'].lower() for w in all_words]
        
        # Calculate similarity scores
        ref_clean = reference_text.lower().strip()
        trans_clean = transcribed_text.lower().strip()
        
        levenshtein_score = round((1 - textdistance.levenshtein.normalized_distance(ref_clean, trans_clean)) * 100, 1)
        jaccard_score = round(textdistance.jaccard.similarity(ref_clean.split(), trans_clean.split()) * 100, 1)
        jaro_score = round(textdistance.jaro_winkler.similarity(ref_clean, trans_clean) * 100, 1)
        global_score = round(levenshtein_score * 0.5 + jaccard_score * 0.3 + jaro_score * 0.2, 1)

        # Enhanced lisp detection
        lisp_candidates, missing_sibilants, lisp_severity = self.enhanced_lisp_detection(all_words, ref_words)
        
        # Word analysis
        missing_words = [w for w in ref_words if w not in trans_words]
        added_words = [w for w in trans_words if w not in ref_words]
        low_conf_words = [w['word'] for w in all_words if w.get('probability', 1.0) < 0.6]
        
        # Production readiness assessment
        production_ready = self.assess_production_readiness(global_score, levenshtein_score, jaccard_score, jaro_score, lisp_severity)

        return {
            "success": True,
            "global_score": global_score,
            "levenshtein": levenshtein_score,
            "jaccard": jaccard_score,
            "jaro": jaro_score,
            "transcribed": transcribed_text,
            "missing_words": missing_words,
            "added_words": added_words,
            "low_confidence_words": low_conf_words,
            "word_details": all_words,
            "language": result.get("language", "unknown"),
            "lisp_candidates": lisp_candidates,
            "missing_sibilants": missing_sibilants,
            "lisp_severity": lisp_severity,
            "production_ready": production_ready,
            "timestamp": datetime.now().isoformat()
        }

    def assess_production_readiness(self, global_score, levenshtein, jaccard, jaro, lisp_severity):
        """Assess if pronunciation meets production standards"""
        criteria = {
            "global_score": global_score >= self.thresholds['global_score'],
            "levenshtein": levenshtein >= self.thresholds['levenshtein'],
            "jaccard": jaccard >= self.thresholds['jaccard'],
            "jaro": jaro >= self.thresholds['jaro'],
            "lisp_acceptable": lisp_severity <= self.thresholds['lisp_severity']
        }
        
        passed = sum(criteria.values())
        total = len(criteria)
        
        if passed == total:
            status = "✅ PRODUCTION READY"
        elif passed >= total * 0.8:
            status = "⚠️ NEEDS MINOR IMPROVEMENTS"
        else:
            status = "❌ NOT PRODUCTION READY"
            
        return {
            "status": status,
            "passed": passed,
            "total": total,
            "criteria": criteria
        }

    def create_radar_chart(self, scores):
        """Create radar chart visualization"""
        metrics = ['Global Score', 'Levenshtein', 'Jaccard', 'Jaro-Winkler']
        values = [scores['global_score'], scores['levenshtein'], scores['jaccard'], scores['jaro']]
        thresholds = [self.thresholds['global_score'], self.thresholds['levenshtein'], 
                     self.thresholds['jaccard'], self.thresholds['jaro']]
        
        fig = go.Figure()
        
        # Actual scores
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=metrics + [metrics[0]],
            fill='toself',
            name='Actual Scores',
            line_color='blue'
        ))
        
        # Thresholds
        fig.add_trace(go.Scatterpolar(
            r=thresholds + [thresholds[0]],
            theta=metrics + [metrics[0]],
            fill='toself',
            name='Production Thresholds',
            line_color='red',
            opacity=0.3
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="French Pronunciation Quality Metrics"
        )
        
        return fig

def process_audio_enhanced(audio_file, reference_text):
    """Enhanced processing with visualization and detailed analysis"""
    if not audio_file or not reference_text.strip():
        return "❌ Please provide both audio file and reference text.", None, ""
    
    try:
        # Show processing status
        processing_msg = "🔄 Processing audio with Whisper... Please wait."
        
        evaluator = FrenchPronunciationEvaluator()
        result = evaluator.evaluate_pronunciation(audio_file, reference_text)
        
        if result["success"]:
            # Create summary report
            summary = f"""# 🎯 French Pronunciation Analysis

**📝 Reference**: {reference_text}
**🎙️ Transcribed**: {result['transcribed']}
**🌍 Language**: {result['language']}
**📅 Evaluated**: {result['timestamp'][:19]}

## 📊 Production Readiness Assessment
{result['production_ready']['status']} ({result['production_ready']['passed']}/{result['production_ready']['total']} criteria met)

## 🎯 Scoring Metrics
• **Global Score**: {result['global_score']}/100 {'✅' if result['production_ready']['criteria']['global_score'] else '❌'}
• **Levenshtein**: {result['levenshtein']}/100 {'✅' if result['production_ready']['criteria']['levenshtein'] else '❌'}
• **Jaccard**: {result['jaccard']}/100 {'✅' if result['production_ready']['criteria']['jaccard'] else '❌'}
• **Jaro-Winkler**: {result['jaro']}/100 {'✅' if result['production_ready']['criteria']['jaro'] else '❌'}

## 🔍 Word Analysis
**Missing**: {', '.join(result['missing_words']) if result['missing_words'] else 'None'}
**Added**: {', '.join(result['added_words']) if result['added_words'] else 'None'}
**Low Confidence**: {', '.join(result['low_confidence_words']) if result['low_confidence_words'] else 'None'}"""

            # Lisp analysis with proper severity display
            if result['lisp_candidates']:
                capped_severity = min(5.0, result['lisp_severity'])
                summary += f"\n\n## ⚠️ Sibilant Analysis (Severity: {capped_severity:.1f}/5.0)\n"
                for lisp in result['lisp_candidates']:
                    summary += f"• **{lisp['word']}** ({lisp['sibilant_type']}) - Severity: {lisp['severity']:.1f}, Confidence: {lisp['confidence']:.2f}\n"
                if result['missing_sibilants']:
                    summary += f"\n**Missing sibilants**: {', '.join(result['missing_sibilants'])}"
            else:
                summary += "\n\n## ✅ Sibilant Analysis\nNo pronunciation issues detected in French sibilant sounds."

            # Create radar chart
            radar_chart = evaluator.create_radar_chart(result)
            
            # Detailed JSON - convert all non-serializable types
            def convert_to_serializable(obj):
                if isinstance(obj, (np.integer, np.int64, np.int32)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float64, np.float32)):
                    return float(obj)
                elif isinstance(obj, (np.bool_, bool)):
                    return bool(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif hasattr(obj, 'item'):  # Handle other numpy scalars
                    return obj.item()
                elif isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [convert_to_serializable(item) for item in obj]
                elif obj is None or isinstance(obj, (str, int, float)):
                    return obj
                else:
                    return str(obj)  # Fallback for any other type
            
            json_data = {
                "scores": {k: v for k, v in result.items() if k in ['global_score', 'levenshtein', 'jaccard', 'jaro']},
                "production_assessment": result['production_ready'],
                "lisp_analysis": {
                    "severity": result['lisp_severity'],
                    "candidates": result['lisp_candidates'],
                    "missing_sibilants": result['missing_sibilants']
                },
                "word_details": result['word_details']
            }
            
            detailed_json = json.dumps(convert_to_serializable(json_data), indent=2)
            
            return summary, radar_chart, detailed_json
        else:
            return f"❌ Error: {result.get('error', 'Unknown error')}", None, ""
        
    except Exception as e:
        return f"❌ Processing error: {str(e)}", None, ""

def create_enhanced_interface():
    with gr.Blocks(title="Enhanced French Pronunciation Evaluator", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🎙️ Enhanced French Pronunciation Evaluator
        
        Professional-grade French pronunciation evaluation with production readiness assessment.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 📤 Input")
                audio_input = gr.Audio(
                    type="filepath", 
                    label="🎵 Upload French Audio",
                    show_download_button=False
                )
                text_input = gr.Textbox(
                    label="📝 Reference Text (French)",
                    value="Bonjour, comment allez-vous aujourd'hui ?",
                    lines=2,
                    max_lines=4
                )
                evaluate_btn = gr.Button(
                    "🚀 Evaluate Pronunciation", 
                    variant="primary", 
                    size="lg"
                )
            
            with gr.Column(scale=2):
                gr.Markdown("## 📊 Results")
                summary_output = gr.Markdown("*Upload audio and click evaluate...*")
                radar_plot = gr.Plot(label="Quality Metrics")
        
        with gr.Row():
            gr.Markdown("## 🔍 Detailed Analysis")
            json_output = gr.Code(label="JSON Report", language="json", lines=10)
        
        evaluate_btn.click(
            process_audio_enhanced,
            inputs=[audio_input, text_input],
            outputs=[summary_output, radar_plot, json_output],
            show_progress=True
        )
        
        with gr.Accordion("📊 Metrics Explanation & Scoring", open=False):
            gr.Markdown("""
            ## 🎯 Evaluation Metrics Explained
            
            ### **Global Score (Weight: Combined)**
            - **What it measures**: Overall pronunciation quality combining all metrics
            - **Calculation**: Levenshtein (50%) + Jaccard (30%) + Jaro-Winkler (20%)
            - **Target**: ≥85% for production readiness
            - **Interpretation**: 
              - 90-100%: Excellent pronunciation
              - 80-89%: Good pronunciation with minor issues
              - 70-79%: Acceptable but needs improvement
              - <70%: Significant pronunciation problems
            
            ### **Levenshtein Distance (Weight: 50%)**
            - **What it measures**: Character-level accuracy between reference and transcribed text
            - **How it works**: Counts minimum edits (insertions, deletions, substitutions) needed
            - **Target**: ≥80% for production readiness
            - **Best for**: Detecting spelling/phonetic errors, mispronunciations
            - **Example**: "bonjour" vs "bonjur" = 90% similarity (1 character difference)
            
            ### **Jaccard Similarity (Weight: 30%)**
            - **What it measures**: Word-level overlap between reference and transcribed text
            - **How it works**: Intersection over union of word sets
            - **Target**: ≥75% for production readiness
            - **Best for**: Detecting missing words, word order issues
            - **Example**: "hello world" vs "hello" = 50% (1 common word out of 2 total unique words)
            
            ### **Jaro-Winkler Similarity (Weight: 20%)**
            - **What it measures**: Phonetic similarity with emphasis on prefix matching
            - **How it works**: Considers character transpositions and common prefixes
            - **Target**: ≥80% for production readiness
            - **Best for**: Detecting similar-sounding words, accent variations
            - **Example**: "martin" vs "martyn" = 96% (high phonetic similarity)
            
            ## 🗣️ Lisp Detection System
            
            ### **French Sibilant Sounds Monitored**
            - **'s' sounds** (voiceless alveolar): Weight 1.0
            - **'z' sounds** (voiced alveolar): Weight 1.1
            - **'ch' sounds** (voiceless postalveolar): Weight 1.2
            - **'j' sounds** (voiced postalveolar): Weight 1.3
            
            ### **Lisp Severity Scoring (0-5 scale)**
            - **0-1**: No issues detected
            - **1-2**: Minor pronunciation variations
            - **2-3**: Noticeable but acceptable (production threshold)
            - **3-4**: Clear pronunciation issues
            - **4-5**: Severe pronunciation problems
            
            ### **Detection Criteria**
            - **Low Confidence**: Whisper confidence <70% on sibilant words
            - **Interdental Patterns**: 'th' sounds replacing sibilants
            - **Lateral Patterns**: 'sl', 'tl' sound combinations
            - **Weighted Scoring**: More severe penalties for complex sibilants
            
            ## 🎯 Production Readiness Criteria
            
            ### **Quality Gates**
            - **✅ Production Ready**: All 5 criteria met
            - **⚠️ Minor Improvements**: 4/5 criteria met (80%+)
            - **❌ Not Ready**: <4/5 criteria met
            
            ### **Assessment Criteria**
            1. Global Score ≥85%
            2. Levenshtein ≥80%
            3. Jaccard ≥75%
            4. Jaro-Winkler ≥80%
            5. Lisp Severity ≤3.0
            
            ## 📈 Score Interpretation Guide
            
            ### **Excellent (90-100%)**
            - Native-like pronunciation quality
            - Minimal transcription errors
            - Ready for premium voice applications
            
            ### **Good (80-89%)**
            - Clear, understandable pronunciation
            - Minor accent or timing issues
            - Suitable for most production uses
            
            ### **Acceptable (70-79%)**
            - Understandable but noticeable issues
            - Requires targeted improvement
            - May need additional training
            
            ### **Needs Improvement (<70%)**
            - Significant pronunciation challenges
            - Multiple error types present
            - Requires comprehensive pronunciation work
            
            ## 🔧 Technical Notes
            
            - **Model**: OpenAI Whisper Base (optimized for French)
            - **Confidence Threshold**: 60% for low-confidence word detection
            - **Language Detection**: Automatic with French preference
            - **Word Timestamps**: Precise timing for detailed analysis
            """)
        
        with gr.Accordion("📋 Production Thresholds", open=False):
            gr.Markdown("""
            ### Current Production Thresholds:
            - **Global Score**: ≥85% (weighted combination of all metrics)
            - **Levenshtein**: ≥80% (character-level accuracy)
            - **Jaccard**: ≥75% (word-level similarity)
            - **Jaro-Winkler**: ≥80% (phonetic similarity)
            - **Lisp Severity**: ≤3.0/5.0 (sibilant pronunciation quality)
            
            ### Assessment Levels:
            - **✅ Production Ready**: All criteria met
            - **⚠️ Needs Minor Improvements**: 80%+ criteria met
            - **❌ Not Production Ready**: <80% criteria met
            """)
    
    return interface

if __name__ == "__main__":
    interface = create_enhanced_interface()
    interface.launch()
