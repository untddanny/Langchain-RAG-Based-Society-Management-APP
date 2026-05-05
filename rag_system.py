"""
RAG System for Society Rules Chatbot
Simplified version using langchain_community
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
CHROMA_DB_PATH = "chroma_db"

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Initialize embeddings (converts text to vectors)
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    logger.info("✅ Embeddings initialized")
except Exception as e:
    logger.warning(f"Embeddings initialization issue: {e}")
    embeddings = None

# Initialize Ollama LLM
try:
    llm = Ollama(model="mistral", base_url="http://localhost:11434")
    logger.info("✅ Ollama LLM initialized")
except Exception as e:
    logger.warning(f"Ollama initialization issue: {e}")
    llm = None

# Initialize Chroma vector store
try:
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
        collection_name="society_rules"
    )
    logger.info("✅ Chroma vector store initialized")
except Exception as e:
    logger.warning(f"Chroma initialization issue: {e}")
    vectorstore = None

def load_and_index_document(file_path):
    """
    Load a document and add it to the vector store.
    """
    
    try:
        file_path = str(file_path)
        logger.info(f"Loading document: {file_path}")
        
        # Load document based on file type
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path, encoding='utf-8')
        elif file_path.endswith('.docx'):
            # For DOCX files, extract text first
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                # Create temporary txt file
                temp_path = file_path.replace('.docx', '_temp.txt')
                with open(temp_path, 'w') as f:
                    f.write(text)
                loader = TextLoader(temp_path, encoding='utf-8')
            except:
                raise ValueError("Error processing DOCX file")
        else:
            raise ValueError("Only PDF, TXT, and DOCX files are supported")
        
        # Load documents
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} pages")
        
        # Split into chunks
        text_splitter = CharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separator="\n"
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Add to vector store
        if vectorstore is None:
            raise Exception("Vector store not initialized")
        
        vectorstore.add_documents(chunks)
        logger.info(f"✅ Indexed {len(chunks)} chunks successfully")
        
        return len(chunks)
        
    except Exception as e:
        logger.error(f"Error loading document: {str(e)}")
        raise

def query_rules(question, num_sources=3):
    """
    Answer a question based on indexed documents.
    """
    
    try:
        if vectorstore is None:
            return "Vector store not initialized. Please upload a document first."
        
        if llm is None:
            return "Ollama LLM not available. Make sure Ollama is running on http://localhost:11434"
        
        logger.info(f"Answering question: {question}")
        
        # Search for similar documents
        search_results = vectorstore.similarity_search(question, k=num_sources)
        
        if not search_results:
            return "No relevant information found in uploaded documents."
        
        # Prepare context from search results
        context = "\n\n".join([doc.page_content for doc in search_results])
        
        # Create prompt
        prompt = f"""Based on the following society rules, answer the question.

Society Rules:
{context}

Question: {question}

Answer:"""
        
        # Get answer from LLM
        logger.info("Calling Ollama LLM...")
        answer = llm.invoke(prompt)
        
        logger.info(f"Generated answer: {str(answer)[:100]}...")
        return answer
        
    except Exception as e:
        logger.error(f"Error querying rules: {str(e)}")
        return f"Error: {str(e)}"

def get_all_indexed_documents():
    """Check if vector store has data."""
    try:
        if vectorstore is None:
            return False
        return True
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

def clear_vector_store():
    """Clear all data from vector store."""
    try:
        import shutil
        if os.path.exists(CHROMA_DB_PATH):
            shutil.rmtree(CHROMA_DB_PATH)
            os.makedirs(CHROMA_DB_PATH, exist_ok=True)
            logger.info("✅ Vector store cleared")
            return True
    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}")
        return False

# Test on import
if __name__ == "__main__":
    print("RAG System ready!")
    print(f"Embeddings: {'✅' if embeddings else '❌'}")
    print(f"LLM (Ollama): {'✅' if llm else '❌'}")
    print(f"Vector Store: {'✅' if vectorstore else '❌'}")
