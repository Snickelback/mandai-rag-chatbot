# Simple RAG Chatbot for Mandai assessment
# Mandai Wildlife Reserve visitor assistant- a virtual chatbot to help with info on the parks
# Uses a local FAISS vector store for retrieval

import os
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from huggingface_hub import InferenceClient



def load_from_website(url):     #to load docs, info
    """Scrape text content from a website."""
    print(f"Loading content from: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")


    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
 
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def load_from_folder(folder_path):
    """Load all .txt files from a local folder."""
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append(Document(page_content=content, metadata={"source": filename}))
    return documents




def split_into_chunks(text, source_name="website"):
    """Split raw text into smaller overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      
        chunk_overlap=50,     
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.create_documents(
        [text],
        metadatas=[{"source": source_name}]
    )
    print(f"Created {len(chunks)} chunks from the document.")
    return chunks



def build_vector_store(chunks):
    """Convert chunks into vector embeddings and store them."""
    print("Building vector store with HuggingFace embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
        # Small, fast, and free model - good for retrieval tasks
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    print("Vector store ready")
    return vector_store


def retrieve_context(vector_store, query, top_k=3):
    """Find the most relevant chunks for a given query."""
    results = vector_store.similarity_search(query, k=top_k)
    # Combine the top results into one context string
    context = "\n\n".join([doc.page_content for doc in results])
    return context


def ask_llm(query, context):
    """Send the query + context to the LLM and get an answer."""

    from groq import Groq

    prompt = f"""You are a friendly and helpful visitor assistant for Mandai Wildlife Reserve in Singapore.
Use the context below to answer the question as helpfully as possible.
If the context contains relevant information, use it to give a full answer.
If the context does not contain enough information, use your general knowledge to still give a helpful answer, but mention that the visitor should check the official Mandai website at www.mandai.com for the most accurate details."

Context:
{context}

Question: {query}

Answer:"""
    import os
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))  

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def main():
    print("Loading Mandy- Mandai AI assistant...")

    urls = [
    # About Mandai
    "https://www.mandai.com/en/about-mandai.html",

    # The Parks
    "https://www.mandai.com/en/singapore-zoo.html",
    "https://www.mandai.com/en/night-safari.html",
    "https://www.mandai.com/en/river-wonders.html",
    "https://www.mandai.com/en/bird-paradise.html",
    "https://www.mandai.com/en/rainforest-wild.html",

    # Plan your visit
    "https://www.mandai.com/en/plan-your-visit.html",
    "https://www.mandai.com/en/getting-here.html",

    # Tickets
    "https://www.mandai.com/en/singapore-zoo/tickets-and-admission.html",
    "https://www.mandai.com/en/night-safari/tickets-and-admission.html",
    "https://www.mandai.com/en/river-wonders/tickets-and-admission.html",
    "https://www.mandai.com/en/bird-paradise/tickets-and-admission.html",

    # Animals & Experiences
    "https://www.mandai.com/en/singapore-zoo/animals-and-zones.html",
    "https://www.mandai.com/en/night-safari/animals-and-zones.html",
    "https://www.mandai.com/en/river-wonders/animals-and-zones.html",
    "https://www.mandai.com/en/bird-paradise/animals-and-zones.html",

    # Dining & Facilities
    "https://www.mandai.com/en/singapore-zoo/dining.html",
    "https://www.mandai.com/en/night-safari/dining.html",

    # Conservation
    "https://www.mandai.com/en/mandai-wildlife-group/conservation.html",
    ]

    all_chunks = []
    for url in urls:
        try:
            raw_text = load_from_website(url)
            chunks = split_into_chunks(raw_text, source_name=url)
            all_chunks.extend(chunks)
            print(f"Loaded: {url}")
        except Exception as e:
            print(f"Skipped {url} — {e}")

    vector_store = build_vector_store(all_chunks)

    print("\nHello, I am  Mandy, your Mandai Wildlife reserves virtual assistant! Ask me anything about our parks and I will try my best to help you. Type 'quit' to exit.\n")

    # main chat loop
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if not user_input:
            continue

        # Retrieve relevant context
        context = retrieve_context(vector_store, user_input, top_k=3)

        # Get answer from LLM
        answer = ask_llm(user_input, context)

        print(f"\nBot: {answer}\n")
        print("-" * 40)


if __name__ == "__main__":
    main()
