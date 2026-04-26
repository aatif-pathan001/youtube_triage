## Youtube_triage
**YouTube Video Triage** is a specialized productivity tool designed for professional self-learners to determine if a long-form video (1–4 hours) is worth their time before they commit to watching it.

Rather than relying on unreliable indicators like "likes" or general descriptions, the application provides a "one-shot" verification of whether a specific topic is covered.

### **Core Purpose**
The app solves the "lost in explanation" problem. It targets professionals (specifically ages 22–27) who spend 5–6 hours weekly on technical tutorials but often find themselves skimming at **2x speed**, only to realize halfway through that a video doesn't actually answer their specific question.

### **Key Features**
* **Topic Verification:** Paste a URL and ask a specific question; the app confirms if the answer exists within the video.
* **Exact Timestamps:** If the topic is present, it provides clickable timestamps to jump directly to the relevant section.
* **Negative Scenario Handling:** If the topic isn't found, the app provides a "Skip" button to quickly move on to a different search result.
* **Interactive breakdown:** Users receive a brief breakdown and teaching summary within **60 seconds** to facilitate immediate decision-making.

### **Strategic Positioning**
Unlike general-purpose chat agents (like ChatGPT or Gemini Pro) or simple summarizers (like Eightify), YouTube Video Triage is built to be:
* **Dedicated:** Focused solely on the "triage" phase of learning.
* **One-Shot:** Delivers exact information without requiring long chat threads.
* **Frictionless:** Designed to work without mandatory logins or browser extensions in its V1.

## Setup

1. Clone the repository  
```bash
   git clone https://github.com/your-username/youtube-triage.git  
   cd youtube-triage
```

2. Create your environment file
```bash
   cp .env.example .env
   # Add your GOOGLE_API_KEY to .env
```

3. Install dependencies
```bash
   pip install -e ".[dev]"
```

4. Verify installation
```bash
   pytest tests/unit/ -v  
   # Expected: 2 passed
```

## Usage
Run the application with a YouTube URL and question:  
python main.py

Expected output: a printed answer based on the video content.