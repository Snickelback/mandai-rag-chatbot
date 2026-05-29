# DESIGN.md — Mandy: Mandai Wildlife Reserve Virtual Assistant

## Overview

Mandy is a RAG (Retrieval-Augmented Generation) chatbot that acts as a friendly visitor assistant for Mandai Wildlife Reserve. It answers questions about the parks, tickets, animals, dining, getting there, and conservation by retrieving real content scraped from the official Mandai website and passing it to an LLM to generate helpful, grounded answers.

---

## Architecture

```
Startup (runs once)
    │
    ▼
[ Load & Scrape ]
  - 19 pages scraped from www.mandai.com using requests + BeautifulSoup
  - Noise removed (scripts, styles, navbars, footers)
    │
    ▼
[ Chunking ]
  - Text split into 500-character overlapping chunks
  - RecursiveCharacterTextSplitter from LangChain
    │
    ▼
[ Embedding & Vector Store ]
  - Chunks converted to vectors using HuggingFace sentence-transformers
  - Stored in FAISS vector store (in-memory)
    │
    ▼
Chat Loop (repeats for every user question)
    │
    ▼
[ Retrieval ]
  - User query converted to vector
  - Top 3 most similar chunks retrieved from FAISS
    │
    ▼
[ Prompt Construction ]
  - Query + retrieved chunks combined into a structured prompt
    │
    ▼
[ LLM — Groq (Llama 3.1 8B) ]
  - Generates a grounded, helpful answer
    │
    ▼
[ Answer returned to User ]
```

---

## Data Sources

19 pages scraped from the official Mandai website covering:

| Category | Pages |
|---|---|
| About Mandai | about-mandai |
| The Parks | Singapore Zoo, Night Safari, River Wonders, Bird Paradise, Rainforest Wild |
| Plan Your Visit | plan-your-visit, getting-here |
| Tickets | Singapore Zoo, Night Safari, River Wonders, Bird Paradise |
| Animals & Zones | Singapore Zoo, Night Safari, River Wonders, Bird Paradise |
| Dining | Singapore Zoo, Night Safari |
| Conservation | mandai-wildlife-group/conservation |

Pages that fail to load are gracefully skipped using a `try/except` block so the chatbot still starts successfully.

---

## Data Retrieval Strategy

### Web Scraping
- `requests.get(url)` fetches the raw HTML of each page
- `BeautifulSoup` parses the HTML and removes noisy tags (`script`, `style`, `nav`, `footer`)
- `get_text()` extracts clean readable text
- Empty lines are stripped to reduce noise in the chunks

### Chunking Strategy
- **Tool:** `RecursiveCharacterTextSplitter` from `langchain_text_splitters`
- **Chunk size:** 500 characters — precise enough for targeted retrieval
- **Overlap:** 50 characters — prevents meaning being lost at chunk boundaries
- **Separators:** `["\n\n", "\n", ".", " "]` — splits on paragraphs first, then lines, then sentences, then words, keeping chunks semantically meaningful

---

## Embeddings

- **Model:** `sentence-transformers/all-MiniLM-L6-v2` via `langchain_community.embeddings.HuggingFaceEmbeddings`
- **Why?** Lightweight, fast, free, and runs locally with no API key needed. Performs well on semantic similarity tasks which is the core of RAG retrieval.
- **How?** Each chunk is converted into a 384-dimensional vector. Semantically similar text produces vectors that are close together in vector space, enabling meaningful search.

---

## Vector Storage

- **Tool:** FAISS (Facebook AI Similarity Search) via `langchain_community.vectorstores`
- **Why?** Free, runs entirely in memory, fast for small to medium document collections, and ideal for prototyping.
- **Retrieval Process:** User query is embedded using the same model, then compared against all stored chunk vectors. Top 3 most similar chunks (`top_k=3`) are returned as context for the LLM.

---

## Prompt Engineering

The system prompt is designed to:
1. Give the chatbot a friendly persona."Mandy", a visitor assistant for Mandai Wildlife Reserve.
2. Instruct it to use retrieved context as the primary source of truth
3. Allow it to fall back on general knowledge if context is insufficient, while directing visitors to www.mandai.com for accuracy.
4. Avoid the overly strict "I don't have enough information" response that made early versions unhelpful.

```
You are a friendly and helpful visitor assistant for Mandai Wildlife Reserve in Singapore.
Use the context below to answer the question as helpfully as possible.
If the context contains relevant information, use it to give a full answer.
If the context does not contain enough information, use your general knowledge to still 
give a helpful answer, but mention that the visitor should check the official Mandai 
website at www.mandai.com for the most accurate details.

Context:
{retrieved chunks}

Question: {user query}

Answer:
```

**Key settings:**
- `temperature=0.3` — factual and consistent responses, not overly creative
- `max_tokens=300` — concise answers without unnecessary verbosity

---

## LLM

- **Provider:** Groq (free tier)
- **Model:** `llama-3.1-8b-instant` — Meta's Llama 3.1 8B model, fast and reliable for instruction-following and question answering
- **Why Groq over HuggingFace Inference API?** HuggingFace's free router had limited model support and inconsistent availability. I ran out of tokens quite early and had to look at alternatives. Groq provides sub-second response times and reliable free access to Llama 3.1.
- **API key:** Loaded securely from environment variable `GROQ_API_KEY` — never hardcoded in the source code

---

## Security

- The Groq API key is stored as an environment variable (`os.environ.get("GROQ_API_KEY")`) and never hardcoded in the source code

---

## Limitations & Future Improvements

| Limitation | Improvement |
|---|---|
| FAISS is in-memory — resets on every restart | Use a persistent vector DB like Pinecone or ChromaDB |
| Re-scrapes all 19 pages on every startup (slow) | Save the vector store to disk and reload it |
| No conversation memory | Add LangChain ConversationBufferMemory for multi-turn chat |
| Some Mandai pages may block scraping | Use official APIs or pre-downloaded content instead |
| Single language (English) | Add multilingual support for tourist visitors |

---

## File Structure

```
mandai-rag-chatbot/
│
├── chatbot.py          # Main RAG chatbot — Mandy visitor assistant
├── requirements.txt    # Python dependencies
├── DESIGN.md           # This file — architecture and design decisions
├── TRANSCRIPT.md       # AI-assisted development conversation transcript
└── README.md           # Project overview and setup instructions
```
