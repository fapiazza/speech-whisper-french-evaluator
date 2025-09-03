# 🎙️ French Pronunciation Evaluator

A Gradio-based web application that evaluates French pronunciation accuracy using OpenAI Whisper, with built-in lisp detection for sibilant sounds.

## 🌟 Features

- **Whisper Transcription**: Uses OpenAI Whisper for accurate French speech recognition
- **Pronunciation Scoring**: Multiple similarity metrics (Levenshtein, Jaccard, Jaro-Winkler)
- **Lisp Detection**: Identifies potential lisp issues in French sibilant sounds (s, z, ch, j, sh)
- **Word-level Analysis**: Detailed timing and confidence scores for each word
- **Error Analysis**: Missing words, added words, and low-confidence predictions

## 🚀 Quick Start

### Hugging Face Spaces
Visit the live demo: [Your Space URL]

### Local Installation

```bash
git clone [your-repo-url]
cd whisper-french-evaluator
pip install -r requirements.txt
python app.py
```

## 📊 How It Works

1. **Upload Audio**: Record or upload a French audio file
2. **Enter Reference**: Provide the expected French text
3. **Get Analysis**: Receive detailed pronunciation evaluation including:
   - Global similarity score
   - Word-level timing and confidence
   - Lisp detection for sibilant sounds
   - Missing/added word analysis

## 🎯 Use Cases

- **Language Learning**: Evaluate French pronunciation progress
- **Speech Therapy**: Detect lisp patterns in French sibilants
- **Education**: Assess student pronunciation accuracy
- **Research**: Analyze French speech patterns

## 📋 Scoring Metrics

- **Global Score**: Weighted combination of all metrics
- **Levenshtein**: Character-level similarity (50% weight)
- **Jaccard**: Word-level similarity (30% weight)  
- **Jaro-Winkler**: Phonetic similarity (20% weight)

## 🔧 Technical Details

- **Model**: OpenAI Whisper Base (French optimized)
- **Framework**: Gradio for web interface
- **Languages**: Optimized for French pronunciation
- **Audio**: Supports common audio formats (WAV, MP3, M4A)

## 📝 Example

**Reference**: "Bonjour, comment allez-vous aujourd'hui ?"
**Audio**: Upload your pronunciation
**Result**: Detailed analysis with scores and lisp detection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- Gradio for the web interface
- TextDistance for similarity metrics
