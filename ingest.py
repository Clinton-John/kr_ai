import os
from langchain_community.document_loaders import PyPDFLoader, JSONLoader, TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings  #Hugging face embeddings
from langchain_community.vectorstores import Chroma

from langchain_community.embeddings import OllamaEmbeddings


# ── 1. Load all documents ──────────────────────────────
docs = []

# PDFs (legislation + guides)
pdf_folders = ["knowledge_base/legislation", "knowledge_base/guides"]
for folder in pdf_folders:
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            path = os.path.join(folder, filename)
            print(f"Loading PDF: {path}")
            loader = PyPDFLoader(path)
            docs.extend(loader.load())

# JSON FAQs
faq_folder = "knowledge_base/faqs"
for filename in os.listdir(faq_folder):
    if filename.endswith(".json") and filename != "all_faqs_combined.json":
        path = os.path.join(faq_folder, filename)
        print(f"Loading FAQs: {path}")
        loader = JSONLoader(
            file_path=path,
            jq_schema=".[]",
            content_key="answer",
            metadata_func=lambda rec, _: {
                "question": rec.get("question", ""),
                "category": rec.get("category", ""),
                "source":   rec.get("source", ""),
            }
        )
        docs.extend(loader.load())

# Deadlines text file
deadline_path = "knowledge_base/deadline/filing_deadlines_2025.txt"
print(f"Loading deadlines: {deadline_path}")
loader = TextLoader(deadline_path)
docs.extend(loader.load())

print(f"\n✓ Total documents loaded: {len(docs)}")

# ── 2. Split into chunks ───────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # characters per chunk
    chunk_overlap=50,      # overlap so context isn't cut off
)
chunks = splitter.split_documents(docs)
print(f"✓ Total chunks created: {len(chunks)}")

# ── 3. Embed and store in ChromaDB ────────────────────
print("\nEmbedding chunks into ChromaDB (this may take a few minutes)...")
# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")   #Hugging face section
embeddings = OllamaEmbeddings(model="nomic-embed-text")
db = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="./chroma_db"
)
print("✓ ChromaDB saved to ./chroma_db")
print(f"✓ Total vectors stored: {db._collection.count()}")