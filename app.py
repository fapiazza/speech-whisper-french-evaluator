#!/usr/bin/env python3

import whisper
import textdistance
import gradio as gr

def detect_lisp_french(all_words, ref_words):
    sibilant_letters = ['s', 'z', 'ch', 'j', 'sh']
    
    def is_sibilant(word):
        w = word.lower()
        return any(sib in w for sib in sibilant_letters)
    
    ref_sibilants = [w for w in ref_words if is_sibilant(w)]
    trans_sibilants = [w['word'].lower() for w in all_words if is_sibilant(w['word'])]
    lisp_candidates = []
    
    for w in all_words:
        word_lower = w['word'].lower()
        if is_sibilant(word_lower):
            if w.get('probability', 1) < 0.7 or 'th' in word_lower:
                lisp_candidates.append({
                    "word": w['word'],
                    "start": w['start'],
                    "end": w['end'],
                    "confidence": w.get('probability',1)
                })
    
    missing_sibilants = [w for w in ref_sibilants if w not in trans_sibilants]
    return lisp_candidates, missing_sibilants

def evaluate_whisper_detailed(audio_file_path, reference_text):
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
    
    missing_words = [w for w in ref_words if w not in trans_words]
    added_words = [w for w in trans_words if w not in ref_words]
    low_conf_words = [w['word'] for w in all_words if w.get('probability', 1.0) < 0.6]
    
    ref_clean = reference_text.lower().strip()
    trans_clean = transcribed_text.lower().strip()
    
    levenshtein_score = round((1 - textdistance.levenshtein.normalized_distance(ref_clean, trans_clean)) * 100, 1)
    jaccard_score = round(textdistance.jaccard.similarity(ref_clean.split(), trans_clean.split()) * 100, 1)
    jaro_score = round(textdistance.jaro_winkler.similarity(ref_clean, trans_clean) * 100, 1)
    global_score = round(levenshtein_score * 0.5 + jaccard_score * 0.3 + jaro_score * 0.2, 1)

    lisp_candidates, missing_sibilants = detect_lisp_french(all_words, ref_words)

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
        "missing_sibilants": missing_sibilants
    }

def process_audio_and_evaluate(audio_file, reference_text):
    if not audio_file or not reference_text.strip():
        return "❌ Please provide both audio file and reference text."
    
    try:
        result = evaluate_whisper_detailed(audio_file, reference_text)
        
        if result["success"]:
            word_table = "| Word | Start | End | Confidence |\n|------|-------|-----|------------|\n"
            for w in result['word_details']:
                word_table += f"| {w['word']} | {w['start']:.2f} | {w['end']:.2f} | {w.get('probability', 1):.2f} |\n"
            
            lisp_output = ""
            if result['lisp_candidates'] or result['missing_sibilants']:
                lisp_output = "\n### ⚠️ Possible Lisp Detected in Sibilant Words\n"
                for item in result['lisp_candidates']:
                    lisp_output += f"- {item['word']} (start: {item['start']:.2f}, end: {item['end']:.2f}, conf: {item['confidence']:.2f})\n"
                if result['missing_sibilants']:
                    lisp_output += f"\nMissing sibilants: {', '.join(result['missing_sibilants'])}\n"
            else:
                lisp_output = "\n✅ No French lisp detected in sibilant words.\n"
            
            output = f"""## 🎯 Whisper Transcription Analysis

**📝 Reference**: {reference_text}

**🎙️ Transcribed**: {result['transcribed']}

**🌍 Language**: {result['language']}

## 📊 Scoring
• **Global Similarity Score**: {result['global_score']}/100
• **Levenshtein score**: {result['levenshtein']}/100  
• **Jaccard score (words)**: {result['jaccard']}/100
• **Jaro-Winkler score**: {result['jaro']}/100

## ❌ Word-level Errors
**Missing words**: {', '.join(result['missing_words']) if result['missing_words'] else 'None'}

**Added words**: {', '.join(result['added_words']) if result['added_words'] else 'None'}

**Low-confidence words**: {', '.join(result['low_confidence_words']) if result['low_confidence_words'] else 'None'}

{lisp_output}

## 📋 Word-level Details
{word_table}"""
        else:
            output = f"❌ Error: {result['error']}"
        
        return output
        
    except Exception as e:
        return f"❌ Processing error: {str(e)}"

def create_interface():
    with gr.Blocks(title="French Pronunciation Evaluator", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🎙️ French Pronunciation Evaluator
        
        Upload an audio file and provide reference text to evaluate French pronunciation accuracy using OpenAI Whisper.
        Includes lisp detection for sibilant sounds (s, z, ch, j, sh).
        """)
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(type="filepath", label="🎵 Upload Audio File")
                text_input = gr.Textbox(
                    label="📝 Reference Text (French)",
                    value="Bonjour, comment allez-vous aujourd'hui ?",
                    lines=3,
                    placeholder="Enter the expected French text..."
                )
                evaluate_btn = gr.Button("🚀 Evaluate Pronunciation", variant="primary", size="lg")
            
            with gr.Column():
                results_output = gr.Markdown("*Upload audio and click evaluate to see results...*")
        
        evaluate_btn.click(
            process_audio_and_evaluate,
            inputs=[audio_input, text_input],
            outputs=results_output
        )
        
        gr.Markdown("""
        ### How it works:
        1. **Upload** your French audio recording
        2. **Enter** the reference text (what should have been said)
        3. **Click** evaluate to get detailed pronunciation analysis
        
        The tool provides similarity scores, word-level analysis, and lisp detection for French sibilant sounds.
        """)
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch()
