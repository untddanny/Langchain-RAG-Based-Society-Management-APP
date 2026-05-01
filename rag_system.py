from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
import os

# Paths
UPLOAD_FOLDER = "uploads"
CHROMA_DB_PATH = "chroma_db"

# Initialize embeddings (converts text to vectors)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize Ollama LLM
llm = Ollama(model="mistral", base_url="http://localhost:11434")

# Initialize Chroma vector store
vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory=CHROMA_DB_PATH
)

def load_and_index_document(file_path):
    """
    Load document, chunk it, and add to vector store
    
    Steps:
    1. Load document (PDF or TXT)
    2. Split into chunks (500 chars with 50 char overlap)
    3. Add chunks to Chroma
    """
    
    # Load document
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Only PDF and TXT supported")
    
    documents = loader.load()
    
    # Split into chunks
    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    
    # Add to vector store
    vectorstore.add_documents(chunks)
    print(f"✅ Indexed {len(chunks)} chunks from {file_path}")

def query_rules(question):
    """
    Answer question based on uploaded documents
    
    Steps:
    1. Search for similar chunks in Chroma
    2. Pass chunks + question to Ollama
    3. Return answer
    """
    
    # Create RAG chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
    )
    
    # Get answer
    answer = qa.run(question)
    return answer

# Create uploads folder if doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)