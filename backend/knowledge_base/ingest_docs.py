import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

def ingest():
    docs_dir = os.path.join(os.path.dirname(__file__), "docs")
    db_dir = os.path.join(os.path.dirname(__file__), "vector_db")
    
    pdf_files = glob.glob(os.path.join(docs_dir, "*.pdf"))
    if not pdf_files:
        print("Nenhum PDF encontrado na pasta docs.")
        return

    all_pages = []
    print("Iniciando leitura dos PDFs...")
    for pdf in pdf_files:
        print(f"Lendo: {os.path.basename(pdf)}")
        loader = PyPDFLoader(pdf)
        pages = loader.load()
        all_pages.extend(pages)
        
    print(f"Total de páginas lidas: {len(all_pages)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(all_pages)
    print(f"Total de chunks gerados: {len(chunks)}")
    
    # Removido check de GEMINI_API_KEY pois o HuggingFaceEmbeddings roda localmente

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Gerando embeddings via Google e salvando no ChromaDB (isso pode levar alguns instantes)...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_dir
    )
    
    print("Ingestão concluída com sucesso! Banco vetorial salvo em", db_dir)

if __name__ == "__main__":
    ingest()
