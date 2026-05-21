# SIMPLIFIED RAG SYSTEM - NO PYTORCH DEPENDENCY
# Uses Ollama directly with simple text search

# IMPORT OS FOR FILE OPERATIONS
import os
# IMPORT LOGGING FOR ERROR MESSAGES
import logging

# SET PATHS
UPLOAD_FOLDER = "uploads"
CHROMA_DB_PATH = "chroma_db"

# CREATE FOLDERS IF DON'T EXIST
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# TRY TO IMPORT OLLAMA
try:
    # IMPORT OLLAMA LLM
    from langchain_community.llms import Ollama
except ImportError:
    try:
        from langchain.llms import Ollama
    except ImportError:
        Ollama = None
        logging.warning("Ollama not available")

# INITIALIZE OLLAMA LLM - LOCAL LANGUAGE MODEL
# Connects to Ollama server running on localhost:11434
try:
    llm = Ollama(model="mistral", base_url="http://localhost:11434")
except Exception as e:
    logging.warning(f"Could not initialize Ollama: {e}")
    llm = None

# STORAGE FOR INDEXED DOCUMENTS (IN-MEMORY)
# In production, use real database, but for learning this works
indexed_documents = {}
document_chunks = {}


def load_and_index_document(file_path):
    """
    Load document and store in memory for searching
    
    Process:
    1. Load document (PDF or TXT)
    2. Split into chunks
    3. Store in memory with filename
    """
    
    # GET FILENAME WITHOUT PATH
    filename = os.path.basename(file_path)
    
    # READ DOCUMENT CONTENT
    if file_path.endswith('.pdf'):
        # PDF SUPPORT - REQUIRES pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
        except ImportError:
            raise ImportError("PDF support requires: pip install pypdf")
    elif file_path.endswith('.txt'):
        # SIMPLE TEXT FILE READING
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        raise ValueError("Only TXT and PDF files supported")
    
    # SPLIT CONTENT INTO CHUNKS (500 characters each with overlap)
    chunk_size = 500
    chunk_overlap = 50
    chunks = []
    
    # CREATE OVERLAPPING CHUNKS
    for i in range(0, len(content), chunk_size - chunk_overlap):
        chunk = content[i:i + chunk_size]
        if chunk.strip():  # ONLY ADD NON-EMPTY CHUNKS
            chunks.append(chunk)
    
    # STORE CHUNKS IN MEMORY
    if chunks:
        indexed_documents[filename] = {
            'path': file_path,
            'content': content,
            'chunks': chunks,
            'chunk_count': len(chunks)
        }
        document_chunks[filename] = chunks
        print(f"✅ Indexed {len(chunks)} chunks from {filename}")
        return True
    else:
        raise ValueError("No text content found in document")


def query_rules(question):
    """
    Answer question based on uploaded documents
    
    Process:
    1. Search all documents for relevant sections
    2. Combine best matches as context
    3. Send to Ollama with explicit instructions
    4. Return answer based on context
    """
    
    # CHECK IF ANY DOCUMENTS ARE INDEXED
    if not indexed_documents:
        return "No documents uploaded yet. Please upload a document first in Management Documents."
    
    # SEARCH ALL CHUNKS FOR RELEVANCE (SIMPLE KEYWORD SEARCH)
    relevant_chunks = []
    question_words = set(question.lower().split())
    
    # SCORE EACH CHUNK BASED ON MATCHING WORDS
    for filename, doc_info in indexed_documents.items():
        for chunk in doc_info['chunks']:
            # COUNT HOW MANY QUESTION WORDS APPEAR IN CHUNK
            chunk_lower = chunk.lower()
            score = sum(1 for word in question_words if word in chunk_lower)
            
            # ADD CHUNK WITH SCORE IF IT HAS MATCHES
            if score > 0:
                relevant_chunks.append((chunk, score))
    
    # IF NO RELEVANT CHUNKS FOUND, SEARCH BY CONTENT TYPE
    if not relevant_chunks:
        # RETURN ALL CHUNKS (FALLBACK)
        for filename, doc_info in indexed_documents.items():
            for chunk in doc_info['chunks'][:3]:  # LIMIT TO FIRST 3
                relevant_chunks.append((chunk, 1))
    
    # SORT BY RELEVANCE SCORE (HIGHEST FIRST)
    relevant_chunks.sort(key=lambda x: x[1], reverse=True)
    
    # TAKE TOP 5 MOST RELEVANT CHUNKS
    top_chunks = relevant_chunks[:5]
    
    # IF STILL NO CHUNKS, RETURN ERROR
    if not top_chunks:
        return "No relevant information found. Please upload documents with society rules."
    
    # COMBINE CHUNKS INTO CONTEXT
    context = "\n\n".join([chunk for chunk, score in top_chunks])
    
    # CHECK IF OLLAMA IS AVAILABLE
    if llm is None:
        # NO OLLAMA - RETURN CONTEXT DIRECTLY
        return f"[No Ollama - Raw context]\n\n{context[:500]}..."
    
    # CREATE EXPLICIT PROMPT FOR LLM
    prompt = f"""You are a helpful assistant for society management. Answer questions about society rules.

IMPORTANT:
- Answer ONLY based on the provided context below
- Do NOT use your general knowledge
- If the answer is not in the context, say "This information is not available in the society rules"
- Be specific and cite the rule when possible

CONTEXT FROM SOCIETY RULES:
{context}

QUESTION: {question}

ANSWER:"""
    
    # SEND TO OLLAMA AND GET ANSWER
    try:
        answer = llm.invoke(prompt)
        return answer
    except Exception as e:
        # IF OLLAMA ERROR, RETURN CONTEXT
        return f"Error contacting LLM: {str(e)}\n\nRelevant context:\n{context[:300]}..."


def get_indexed_documents():
    """
    Get list of all indexed documents
    
    Returns:
    - List of filenames that are indexed
    """
    return list(indexed_documents.keys())


def clear_documents():
    """
    Clear all indexed documents from memory
    
    Use this to reset the system
    """
    global indexed_documents, document_chunks
    indexed_documents = {}
    document_chunks = {}
    print("✅ Cleared all indexed documents")
