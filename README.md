# mandai-rag-chatbot
# Mandy the Mandai Wildlife Reserve Virtual Assistant

A RAG (Retrieval-Augmented Generation) chatbot that acts as a friendly visitor assistant for Mandai Wildlife Reserve. Mandy answers questions about the parks, tickets, animals, dining, getting there, and conservation by retrieving real content from the official Mandai website.

Built for the Mandai Wildlife Group AI Specialist assessment using free, open-source tools.

## What Mandy Can Answer

- "What animals can I see at Singapore Zoo?"
- "How do I get to Mandai Wildlife Reserve?"
- "What time does Night Safari open?"
- "Tell me about conservation efforts at Mandai"
- "What dining options are available at Bird Paradise?"
- "How much are the tickets?"

## Setup & Run

**1. Clone the repo**
```bash
git clone https://github.com/your-username/mandai-rag-chatbot.git
cd mandai-rag-chatbot
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set your Groq API key as an environment variable**

Get a free key at https://console.groq.com, then run:
```powershell
$env:GROQ_API_KEY = "gsk_your_key_here"
```

**5. Run Mandy**
```bash
python chatbot.py
```



## Files

| File | Description |
|---|---|
| `chatbot.py` | Main RAG chatbot — Mandy visitor assistant |
| `requirements.txt` | Python dependencies |
| `DESIGN.md` | Architecture, prompt engineering, and data strategy |
| `TRANSCRIPT.md` | AI-assisted development conversation transcript |

---

## Design Decisions

See `DESIGN.md` for a full breakdown of chunking strategy, embedding choices, vector storage, prompt engineering, and future improvements.
