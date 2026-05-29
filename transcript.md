# TRANSCRIPT.md — AI-Assisted Development Conversation

> This is the transcript of my conversation with Claude (AI assistant) while designing and building Mandy, the Mandai Wildlife Reserve virtual assistant chatbot. My final instruction to claude was to build this transcript file of everything we talked about.

---

**Me:** I need to build a simple RAG chatbot that can answer questions from a website or a library of documents. I want to use free tools as I dont have an OpenAI API key right now. What stack should I use?

**Claude:** Great project! For a free stack, here's what I'd recommend:

- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` from HuggingFace — lightweight, fast, and runs locally with no API key needed.
- **Vector store:** FAISS — free, runs in memory, great for small to medium document collections.
- **LLM:** Groq's free API using Llama 3.1 8B — fast, reliable, and free.
- **Orchestration:** LangChain for chunking, embedding, and retrieval.

This stack is completely free and good enough for a working prototype.

---

**Me:** How should I do the chunking? Could you give size info?

**Claude:** Use LangChain's `RecursiveCharacterTextSplitter` with:

- **Chunk size:** 500 characters — small enough to be precise, large enough to contain meaningful content.
- **Overlap:** 50 characters — ensures a sentence split across two chunks doesn't lose context at the boundary.
- **Separators:** `["\n\n", "\n", ".", " "]` — splits on paragraphs first, then lines, then sentences, keeping chunks semantically meaningful.

---

**Me:** How do I make sure the LLM isnt making things up and only answering from the retrieved context?

**Claude:** This is controlled through your prompt. Tell the model explicitly to use only the provided context:

```
You are a helpful assistant. Answer the user's question using ONLY the information provided below.
If the answer is not in the context, say "I don't have enough information to answer that."
```

Also set `temperature=0.3` — lower temperature makes the model more conservative and factual.

---

**Me:** The chatbot keeps saying "I don't have enough information" even when the answer should be there. How do I fix the prompt?

**Claude:** The prompt is too strict. Try giving it a persona and allowing it to use general knowledge as a fallback:

```
You are a friendly and helpful visitor assistant for Mandai Wildlife Reserve in Singapore.
Use the context below to answer the question as helpfully as possible.
If the context contains relevant information, use it to give a full answer.
If the context does not contain enough information, use your general knowledge to still 
give a helpful answer, but mention that the visitor should check the official Mandai 
website at www.mandai.com for the most accurate details.
```

This makes the chatbot much more useful while still grounding it in real retrieved data.

---

**Me:** I am scraping a website as my data source. The text has a lot of noise, like the header and stuff. How do I clean it up?

**Claude:** Use BeautifulSoup to remove noisy tags before extracting text:

```python
for tag in soup(["script", "style", "nav", "footer"]):
    tag.decompose()

text = soup.get_text(separator="\n")
lines = [line.strip() for line in text.splitlines() if line.strip()]
clean_text = "\n".join(lines)
```

This removes scripts, styles, navigation menus, and footers, then strips empty lines. The remaining text will be much cleaner and retrieval accuracy will improve.

---

**Me:** The chatbot only scraped one page and got 15 chunks which is not enough. How do I feed it more data?

**Claude:** Loop through a list of URLs and combine all the chunks before building the vector store:

```python
all_chunks = []
for url in urls:
    try:
        raw_text = load_from_website(url)
        chunks = split_into_chunks(raw_text, source_name=url)
        all_chunks.extend(chunks)
    except Exception as e:
        print(f"Skipped {url} — {e}")

vector_store = build_vector_store(all_chunks)
```

The `try/except` means any page that fails to load gets skipped silently so the chatbot still starts successfully.

---

**Me:** I need to make this file public. How should I handle the API key so that I dont expose it to everyone and compromise myself?

**Claude:** Never hardcode the key in your source code. Use an environment variable instead:

```python
import os
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
```

Then set it in PowerShell before running:
```powershell
$env:GROQ_API_KEY = "gsk_your_key_here"
```

Also add a `.gitignore` file that excludes `venv/` and `.env` so they never get pushed to GitHub.

---

**Me:** What are the main limitations of this approach and how would I improve it for production?

**Claude:** The main limitations and improvements are:

1. **FAISS is in-memory** — resets every restart. For production, use Pinecone, Weaviate, or ChromaDB for persistence.
2. **Re-scrapes on every startup** — slow. Save the vector store to disk and reload it instead of rebuilding each time.
3. **No conversation memory** — treats every question independently. Add LangChain's `ConversationBufferMemory` for multi-turn chat.
4. **English only** — add multilingual support for international visitors.
5. **Scraping can be blocked** — use official APIs or pre-downloaded content for reliability in production.

---

**Me:** Could you generate an entire transcript of what we talked about here as a .md file I can upload on my github?

**Claude:** Absolutely! A transcript is a great way to show your thought process and how you used AI as a tool to build the chatbot. The file is ready to download!

*End of transcript.*
