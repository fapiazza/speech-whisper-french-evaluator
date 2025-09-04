# French Voice Evaluation Gradio UI

## Installation Requirements

```python
pip install gradio
pip install librosa
pip install numpy
pip install pandas
pip install plotly
pip install scipy
```

## Main Application Code

```python
import gradio as gr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import random

class FrenchVoiceEvaluator:
    def __init__(self):
        self.production_thresholds = {
            'PAS': 95.0,  # Pronunciation Accuracy Score
            'MOS': 4.2,   # Mean Opinion Score
            'PQI': 4.0,   # Prosodic Quality Index
            'FDR': 2.0,   # Fluency Disruption Rate (lower is better)
            'RACS': 90.0, # Regional Accent Consistency Score
            'EIRA': 85.0  # Emotion and Intent Recognition Accuracy
        }
        
    def simulate_pronunciation_analysis(self, audio_file, text_input):
        """Simulate PAS calculation - in production this would use MFA or similar"""
        if audio_file is None and not text_input:
            return 0.0, "No input provided"
        
        # Simulate analysis based on text complexity and length
        base_score = random.uniform(92, 98)
        
        # Enhanced lisp detection simulation
        lisp_analysis = self._simulate_lisp_detection(text_input)
        
        if text_input:
            # Penalize for complex French linguistic features
            complex_features = ['qu\'', 'tion', 'eux', 'aient', 'oient']
            penalty = sum(2 for feature in complex_features if feature in text_input.lower())
            base_score = max(85, base_score - penalty)
            
            # Apply lisp penalties
            base_score -= lisp_analysis['total_penalty']
        
        base_score = max(70, base_score)  # Floor score
        
        details = f"Phoneme accuracy: {base_score:.1f}%\nLiaison patterns: {'Correct' if base_score > 93 else 'Issues detected'}\n{lisp_analysis['details']}"
        return base_score, details

    def _simulate_lisp_detection(self, text_input):
        """Enhanced lisp detection simulation with multiple types"""
        
        # French sibilant phonemes and their characteristics
        french_sibilants = {
            's': {'type': 'voiceless_alveolar', 'weight': 1.0},
            'z': {'type': 'voiced_alveolar', 'weight': 1.1},
            'ʃ': {'type': 'voiceless_postalveolar', 'weight': 1.2},  # 'sh' sound
            'ʒ': {'type': 'voiced_postalveolar', 'weight': 1.3},     # 'j' sound
            'ç': {'type': 'voiceless_palatal', 'weight': 0.8}        # rare in French
        }
        
        # Simulate different types of lisps
        lisp_types = {
            'interdental': {'probability': 0.08, 'severity_range': (1.5, 4.0), 'affects': ['s', 'z']},
            'lateral': {'probability': 0.04, 'severity_range': (2.0, 4.5), 'affects': ['s', 'z', 'ʃ', 'ʒ']},
            'palatal': {'probability': 0.03, 'severity_range': (1.0, 3.5), 'affects': ['ʃ', 'ʒ']},
            'distortion': {'probability': 0.05, 'severity_range': (1.0, 3.0), 'affects': ['s', 'z', 'ʃ', 'ʒ']}
        }
        
        detected_lisps = []
        total_penalty = 0.0
        
        # Check for each lisp type
        for lisp_type, config in lisp_types.items():
            if random.random() < config['probability']:
                severity = random.uniform(*config['severity_range'])
                detected_lisps.append({
                    'type': lisp_type,
                    'severity': severity,
                    'affected_sounds': config['affects']
                })
        
        # Calculate penalties based on text content and detected lisps
        if text_input and detected_lisps:
            text_lower = text_input.lower()
            
            # Count French words with problematic sibilant clusters
            problematic_patterns = [
                'ss', 'sc', 'sch', 'sp', 'st', 'str', 'squ', 'sw',  # s-clusters
                'ch', 'sh', 'tion', 'sion',  # sh/zh sounds
                'j', 'ge', 'gi',  # j sounds
                'c', 'ç', 'ce', 'ci'  # various c sounds
            ]
            
            pattern_count = sum(text_lower.count(pattern) for pattern in problematic_patterns)
            
            for lisp in detected_lisps:
                # Base penalty for lisp presence
                base_penalty = lisp['severity'] * 0.8
                
                # Additional penalty based on affected sounds in text
                affected_penalty = 0
                for sound in lisp['affected_sounds']:
                    if sound in ['s', 'z']:
                        affected_penalty += text_lower.count('s') * 0.3 + text_lower.count('z') * 0.3
                    elif sound in ['ʃ', 'ʒ']:
                        affected_penalty += (text_lower.count('ch') + text_lower.count('j')) * 0.4
                
                # Pattern-based penalty
                pattern_penalty = pattern_count * lisp['severity'] * 0.2
                
                lisp_penalty = min(15.0, base_penalty + affected_penalty + pattern_penalty)  # Cap penalty
                total_penalty += lisp_penalty
        
        # Generate detailed report
        if detected_lisps:
            lisp_details = []
            for lisp in detected_lisps:
                lisp_details.append(f"{lisp['type'].title()} lisp (severity: {lisp['severity']:.1f}/5.0)")
            
            details = f"Sibilant Analysis: {len(detected_lisps)} lisp(s) detected\n"
            details += f"Types: {', '.join([l['type'] for l in detected_lisps])}\n"
            details += f"Impact: -{total_penalty:.1f} points from PAS score\n"
            details += f"Affected sounds: {set().union(*[l['affected_sounds'] for l in detected_lisps])}"
        else:
            details = "Sibilant Analysis: No lisps detected\nSibilant production: Normal\nFrench fricative quality: Good"
        
        return {
            'detected': len(detected_lisps) > 0,
            'types': [l['type'] for l in detected_lisps],
            'total_penalty': total_penalty,
            'details': details,
            'count': len(detected_lisps)
        }

    def simulate_mos_evaluation(self, audio_file, evaluator_count=10):
        """Simulate MOS scoring from multiple evaluators"""
        if audio_file is None:
            return 0.0, "No audio file provided"
            
        # Simulate individual evaluator scores
        scores = np.random.normal(4.3, 0.4, evaluator_count)
        scores = np.clip(scores, 1, 5)  # Ensure scores are in valid range
        
        mean_score = np.mean(scores)
        std_dev = np.std(scores)
        
        details = f"Evaluators: {evaluator_count}\nMean: {mean_score:.2f}\nStd Dev: {std_dev:.2f}\nRange: {min(scores):.1f} - {max(scores):.1f}"
        return mean_score, details

    def simulate_prosodic_analysis(self, audio_file, text_input):
        """Simulate PQI calculation"""
        if audio_file is None:
            return 0.0, "No audio file provided"
            
        # Simulate different prosodic components
        rhythm_score = random.uniform(3.8, 4.5)
        intonation_score = random.uniform(3.9, 4.4)
        pause_score = random.uniform(4.0, 4.6)
        rate_score = random.uniform(3.7, 4.3)
        
        overall_pqi = (rhythm_score + intonation_score + pause_score + rate_score) / 4
        
        details = f"Rhythm: {rhythm_score:.2f}\nIntonation: {intonation_score:.2f}\nPause Placement: {pause_score:.2f}\nSpeaking Rate: {rate_score:.2f}"
        return overall_pqi, details

    def simulate_fluency_analysis(self, audio_file):
        """Simulate FDR calculation"""
        if audio_file is None:
            return 0.0, "No audio file provided"
            
        # Simulate disruption detection
        disruption_rate = random.uniform(0.5, 3.5)
        disruption_types = []
        
        if disruption_rate > 2.0:
            disruption_types.extend(["Unnatural pauses", "Incorrect liaison"])
        if disruption_rate > 2.5:
            disruption_types.append("Choppy delivery")
        if disruption_rate > 3.0:
            disruption_types.append("Mispronounced contractions")
            
        details = f"Disruption Rate: {disruption_rate:.1f}%\nIssues: {', '.join(disruption_types) if disruption_types else 'None detected'}"
        return disruption_rate, details

    def simulate_regional_consistency(self, audio_file, target_variant="European French"):
        """Simulate RACS calculation"""
        if audio_file is None:
            return 0.0, "No audio file provided"
            
        consistency_score = random.uniform(87, 96)
        
        details = f"Target Variant: {target_variant}\nConsistency: {consistency_score:.1f}%\nVowel System: {'Consistent' if consistency_score > 90 else 'Mixed patterns detected'}"
        return consistency_score, details

    def simulate_emotion_recognition(self, audio_file, text_input):
        """Simulate EIRA calculation"""
        if audio_file is None:
            return 0.0, "No audio file provided"
            
        accuracy = random.uniform(82, 92)
        
        # Analyze text for emotional cues
        emotion_cues = {
            'informational': ['weather', 'time', 'information'],
            'empathetic': ['sorry', 'understand', 'help'],
            'urgent': ['immediately', 'urgent', 'emergency']
        }
        
        detected_emotion = "neutral"
        if text_input:
            for emotion, cues in emotion_cues.items():
                if any(cue in text_input.lower() for cue in cues):
                    detected_emotion = emotion
                    break
        
        details = f"Accuracy: {accuracy:.1f}%\nDetected Intent: {detected_emotion}\nProsodic Match: {'Good' if accuracy > 85 else 'Needs improvement'}"
        return accuracy, details

def create_evaluation_interface():
    evaluator = FrenchVoiceEvaluator()
    
    def run_comprehensive_evaluation(audio_file, text_input, evaluator_count):
        """Run all evaluation metrics"""
        results = {}
        details = {}
        
        # Run all evaluations
        pas_score, pas_details = evaluator.simulate_pronunciation_analysis(audio_file, text_input)
        mos_score, mos_details = evaluator.simulate_mos_evaluation(audio_file, evaluator_count)
        pqi_score, pqi_details = evaluator.simulate_prosodic_analysis(audio_file, text_input)
        fdr_score, fdr_details = evaluator.simulate_fluency_analysis(audio_file)
        racs_score, racs_details = evaluator.simulate_regional_consistency(audio_file)
        eira_score, eira_details = evaluator.simulate_emotion_recognition(audio_file, text_input)
        
        results = {
            'PAS': pas_score,
            'MOS': mos_score,
            'PQI': pqi_score,
            'FDR': fdr_score,
            'RACS': racs_score,
            'EIRA': eira_score
        }
        
        details = {
            'PAS': pas_details,
            'MOS': mos_details,
            'PQI': pqi_details,
            'FDR': fdr_details,
            'RACS': racs_details,
            'EIRA': eira_details
        }
        
        # Create summary report
        summary = create_summary_report(results, evaluator.production_thresholds)
        
        # Create visualization
        viz = create_metrics_visualization(results, evaluator.production_thresholds)
        
        return summary, viz, json.dumps(details, indent=2)
    
    def create_summary_report(results, thresholds):
        """Create a summary report with pass/fail indicators"""
        report = "# French Voice Evaluation Results\n\n"
        report += f"**Evaluation Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Overall status
        passes = 0
        total = 0
        
        for metric, score in results.items():
            threshold = thresholds[metric]
            if metric == 'FDR':  # Lower is better for FDR
                passed = score <= threshold
            else:  # Higher is better for others
                passed = score >= threshold
            
            if passed:
                passes += 1
            total += 1
            
            status = "✅ PASS" if passed else "❌ FAIL"
            report += f"**{metric}**: {score:.2f} | Target: {'≤' if metric == 'FDR' else '≥'}{threshold} | {status}\n"
        
        report += f"\n**Overall Status**: {passes}/{total} metrics passed\n"
        
        if passes == total:
            report += "\n🎉 **PRODUCTION READY** - All metrics meet requirements!"
        elif passes >= total * 0.8:
            report += "\n⚠️ **NEEDS MINOR IMPROVEMENTS** - Most metrics acceptable"
        else:
            report += "\n🚫 **NOT PRODUCTION READY** - Multiple metrics below threshold"
            
        return report
    
    def create_metrics_visualization(results, thresholds):
        """Create a radar chart visualization of the metrics"""
        metrics = list(results.keys())
        scores = list(results.values())
        targets = [thresholds[m] for m in metrics]
        
        # Normalize FDR for visualization (invert since lower is better)
        normalized_scores = []
        normalized_targets = []
        
        for i, metric in enumerate(metrics):
            if metric == 'FDR':
                # For FDR, convert to "success rate" (100 - rate)
                normalized_scores.append(100 - scores[i])
                normalized_targets.append(100 - targets[i])
            else:
                normalized_scores.append(scores[i])
                normalized_targets.append(targets[i])
        
        fig = go.Figure()
        
        # Add actual scores
        fig.add_trace(go.Scatterpolar(
            r=normalized_scores + [normalized_scores[0]],  # Close the polygon
            theta=metrics + [metrics[0]],
            fill='toself',
            name='Actual Scores',
            line_color='blue'
        ))
        
        # Add target thresholds
        fig.add_trace(go.Scatterpolar(
            r=normalized_targets + [normalized_targets[0]],
            theta=metrics + [metrics[0]],
            fill='toself',
            name='Target Thresholds',
            line_color='red',
            opacity=0.3
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="French Voice Quality Metrics"
        )
        
        return fig
    
    # Create Gradio interface
    with gr.Blocks(title="French Voice Evaluation for Alexa", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎙️ French Voice Evaluation System")
        gr.Markdown("Upload audio files and evaluate French voice quality against production readiness criteria")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Input")
                audio_input = gr.Audio(
                    label="Upload French Audio Sample",
                    type="filepath"
                )
                text_input = gr.Textbox(
                    label="Text Content (if available)",
                    placeholder="Enter the French text that should be spoken...",
                    lines=3
                )
                evaluator_count = gr.Slider(
                    minimum=5,
                    maximum=50,
                    value=10,
                    step=5,
                    label="Number of Human Evaluators (for MOS)"
                )
                
                evaluate_btn = gr.Button("🔍 Run Comprehensive Evaluation", variant="primary")
            
            with gr.Column(scale=2):
                gr.Markdown("## Results")
                summary_output = gr.Markdown(label="Summary Report")
                metrics_plot = gr.Plot(label="Metrics Visualization")
                
        with gr.Row():
            gr.Markdown("## Detailed Analysis")
            details_output = gr.Code(
                label="Detailed Metrics Breakdown",
                language="json"
            )
        
        # Connect the evaluation function
        evaluate_btn.click(
            fn=run_comprehensive_evaluation,
            inputs=[audio_input, text_input, evaluator_count],
            outputs=[summary_output, metrics_plot, details_output]
        )
        
        # Add information panel
        with gr.Accordion("📊 Metrics Information", open=False):
            gr.Markdown("""
            ### Evaluation Metrics Explained:
            
            - **PAS (Pronunciation Accuracy Score)**: Phoneme-level accuracy compared to native French (Target: ≥95%)
            - **MOS (Mean Opinion Score)**: Human evaluation of naturalness on 1-5 scale (Target: ≥4.2)
            - **PQI (Prosodic Quality Index)**: Rhythm, intonation, and timing quality (Target: ≥4.0)
            - **FDR (Fluency Disruption Rate)**: Percentage of utterances with disfluencies (Target: ≤2%)
            - **RACS (Regional Accent Consistency)**: Consistency within chosen French variant (Target: ≥90%)
            - **EIRA (Emotion/Intent Recognition Accuracy)**: Appropriate prosodic expression (Target: ≥85%)
            
            ### Production Readiness Criteria:
            - **Must Meet**: PAS ≥95%, MOS ≥4.0, FDR ≤3%
            - **Should Meet**: PQI ≥4.0, RACS ≥90%, EIRA ≥80%
            - **Nice to Have**: MOS ≥4.5, All technical targets met
            """)
    
    return demo

# Launch the application
if __name__ == "__main__":
    demo = create_evaluation_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )
```

## Usage Instructions

1. **Install Dependencies**: Run the pip install commands above
2. **Launch Application**: Run `python french_voice_evaluator.py`
3. **Access Interface**: Open the provided URL (typically http://localhost:7860)

## Key Features

### Input Options
- **Audio Upload**: Upload .wav, .mp3, or other audio files containing French voice samples
- **Text Input**: Provide the expected French text for enhanced analysis
- **Evaluator Count**: Adjust the number of simulated human evaluators for MOS scoring

### Evaluation Metrics
- **Real-time Analysis**: Comprehensive evaluation across all 6 key metrics
- **Visual Dashboard**: Radar chart showing performance against targets
- **Pass/Fail Indicators**: Clear production readiness assessment
- **Detailed Breakdown**: JSON output with metric-specific analysis

### Production Integration Notes

In a production environment, you would replace the simulation functions with:

```python
# Real implementations would integrate with:
- Montreal Forced Alignment (MFA) for PAS
- Amazon's internal human evaluation platform for MOS
- PRAAT or similar acoustic analysis tools for PQI
- Custom disfluency detection algorithms for FDR
- Acoustic feature analysis tools for RACS
- Intent recognition systems for EIRA
```

### Customization Options

- Modify `production_thresholds` to adjust quality gates
- Add new metrics by extending the `FrenchVoiceEvaluator` class
- Customize the UI layout and styling through Gradio themes
- Integrate with Amazon's internal systems for real metric calculation

This interface provides an immediate way to test your French voice evaluation framework and gives stakeholders a clear view of voice quality against your production criteria.