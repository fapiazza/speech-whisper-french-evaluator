# 🚀 Hugging Face Spaces Deployment Template

## Required Files Structure
```
project/
├── app.py              # Main Gradio application
├── requirements.txt    # Dependencies
├── README.md          # With YAML header
└── .gitignore         # Optional
```

## 1. README.md Template (CRITICAL)
```yaml
---
title: Your App Title
emoji: 🎙️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# Your App Documentation
```

## 2. requirements.txt Template
```
gradio==4.44.0
numpy==1.24.3
# Add your specific dependencies
```

## 3. app.py Template
```python
import gradio as gr

def your_function(input):
    return "output"

def create_interface():
    with gr.Blocks(title="Your App") as interface:
        # Your interface code
        pass
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch()
```

## 4. Deployment Steps
1. Create HF Space: https://huggingface.co/new-space
2. Clone locally: `git clone https://huggingface.co/spaces/username/spacename`
3. Add files with YAML header in README
4. Push: `git push origin main`
5. Wait for build (2-5 minutes)

## 5. Common Issues & Fixes
- **Configuration error**: Missing YAML header in README
- **Import errors**: Add missing dependencies to requirements.txt
- **Build fails**: Check logs, usually dependency conflicts

## 6. Quick Deploy Command
```bash
# After creating HF Space
git init
git remote add origin https://huggingface.co/spaces/username/spacename
git add .
git commit -m "Initial commit"
git push -u origin main
```
