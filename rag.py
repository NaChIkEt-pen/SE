import os
import argparse
from typing import List
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuration
SUPPORTED_EXTENSIONS = ['.pdf', '.pptx', '.docx', '.ppt', '.doc']
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
from langchain_core.documents import Document
def load_and_split_documents(directory: str) -> List[Document]:
    """Recursively load and split documents from directory"""
    from langchain_core.documents import Document
    documents = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                file_path = os.path.join(root, file)
                try:
                    if ext == '.pdf':
                        loader = PyPDFLoader(file_path)
                    else:
                        loader = UnstructuredFileLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return text_splitter.split_documents(documents)

def create_vector_store(documents, cache_dir="vector_store"):
    """Create or load FAISS vector store"""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},  # Use CPU for M2 compatibility
        encode_kwargs={'normalize_embeddings': True}
    )
    
    if os.path.exists(cache_dir):
        return FAISS.load_local(cache_dir, embeddings)
    
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(cache_dir)
    return vector_store

def query_llm(query: str, vector_store, llm_type="claude"):
    """Query the vector store and LLM"""
    # Retrieve relevant documents
    relevant_docs = vector_store.similarity_search(query, k=3)
    context = "\n\n".join([d.page_content for d in relevant_docs])
    
    # Create prompt
    prompt = ChatPromptTemplate.from_template(
        "You're a student assistant. Use this context:\n{context}\n\nQuestion: {query}"
    )
    
    # Initialize LLM
    if llm_type.lower() == "claude":
        llm = ChatAnthropic(model_name="claude-3-haiku-20240307")
    elif llm_type.lower() == "gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
    else:
        raise ValueError("Invalid LLM type")
    
    # Generate response
    chain = prompt | llm
    return chain.invoke({"context": context, "query": query}).content

if __name__ == "_main_":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory to process")
    parser.add_argument("--query", help="Query to run")
    parser.add_argument("--llm", choices=["claude", "gemini"], default="claude")
    args = parser.parse_args()

    # Process documents only if vector store doesn't exist
    if not os.path.exists("vector_store"):
        print("Processing documents...")
        docs = load_and_split_documents(args.directory)
        print(f"Loaded {len(docs)} document chunks")
        vector_store = create_vector_store(docs)
    else:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vector_store = FAISS.load_local("vector_store", embeddings)

    if args.query:
        response = query_llm(args.query, vector_store, args.llm)
        print("\nResponse:")
        print(response)