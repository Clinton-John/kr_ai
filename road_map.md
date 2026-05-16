Tech Stack
LLaMA 3 (open model) — more powerful than Mistral for question-answering tasks, has an 8B and 70B version, and has a larger community with better Kenyan language support potential.

LangChain (RAG framework) — better documentation, wider community support, and more integrations than LlamaIndex. Easier to get started with for your use case.

ChromaDB (vector database) — simpler to set up than FAISS, runs fully locally with no server needed, and stores metadata alongside vectors (useful for tagging documents by tax category).

Hosting — start with local GPU for development (free), then move to Google Colab (free tier with T4 GPU) or Hugging Face Spaces (free hosting for demos) when ready to go public.

Build Order
1. Download all the PDFs that are used as the knowledge base
2. Write a Python script using LangChain to chunk and embed them into ChromaDB
3. Run LLaMA 3 locally (via Ollama — free tool) as your LLM
4. Build a simple chat loop that retrieves relevant chunks and generates answers
5. Add a basic web UI (Gradio is free and fast to set up)
6. Deploy to Hugging Face Spaces for free public access


1. Knowledge Base
/knowledge_base
  /legislation
    income_tax_act.pdf
    vat_act.pdf
    excise_duty_act.pdf
    tax_procedures_act.pdf
    kra_act.pdf
  /guides
    taxpayers_handbook.pdf
    vat_brochure.pdf
  /faqs
    customs_faqs.txt
    income_tax_faqs.txt
    vat_faqs.txt
    paye_faqs.txt
  /deadlines
    filing_deadlines_2025.txt   ← manually written, update yearly 

2.Building the RAG Pipeline
