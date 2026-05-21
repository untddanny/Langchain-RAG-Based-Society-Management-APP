# Quick Start Guide - RAG Chatbot (FIXED)

## What Was Wrong ❌
1. **Vague answers** → Now uses explicit prompt telling LLM to use ONLY document context
2. **Missing API** → Added `/api/chat` endpoint
3. **Corrupted code** → Fixed rag_system.py syntax errors
4. **No comments** → Added comments on EVERY line

## What's Fixed ✅
- Better RAG prompting system
- Proper error handling
- Detailed code comments for learning
- Working API endpoint

## Run It Now

### Terminal 1: Start Ollama
```bash
ollama serve
```

### Terminal 2: Start Flask
```bash
cd "/Users/nabeel/Desktop/Python Learning/Society App"
python app.py
```

### Browser: Test It
1. Go to: http://localhost:5050
2. Login as Admin: `admin` / `admin123`
3. Go to: Management Documents → Upload a TXT file with rules
4. Logout and login as Member: `101` / `1234`
5. Go to: Ask about Rules → Ask a question
6. Get answer based on YOUR document!

## Example Test Document

Create `test_rules.txt` with:
```
SOCIETY PARKING RULES:
- Monthly fee: Rs 500 per vehicle
- Members can have 2 spaces
- Visitors can park in lot B

MAINTENANCE CHARGES:
- Monthly: Rs 2000
- Covers cleaning and repairs
- Complaints to admin@society.com

VISITING HOURS:
- Guests allowed 6am to 10pm
- Register at gate
- No loud noise after 10pm
```

Then ask: "What is the parking fee?" → Should answer "Rs 500"

## Why Answers Are Better Now

**Old Way (Bad):**
- Generic LLM chain
- Often made up answers
- Ignored your document

**New Way (Good):**
- Explicit instruction: "Use ONLY this context"
- Searches for relevant chunks (top 5)
- Passes chunks as context to LLM
- LLM generates answer ONLY from context

## Code Changes Made

### rag_system.py - FIXED & COMMENTED
1. Removed corrupted code at end
2. Changed query method:
   - Old: `RetrievalQA.from_chain_type()` (vague)
   - New: Direct `llm.invoke()` with explicit prompt
3. Added constraint: "Answer ONLY based on context"
4. Added line-by-line comments for learning

### app.py - FIXED & COMMENTED
1. Added missing `/api/chat` endpoint
2. Fixed imports (added `jsonify`)
3. Added detailed comments on EVERY line
4. Now properly handles JSON requests from chatbot

## How It Works (5 Steps)

```
1. Admin uploads document → Split into chunks → Convert to vectors
2. Vectors stored in Chroma database
3. Member asks question
4. Question converted to vector → Find top 5 similar chunks
5. Pass chunks + question to Ollama with strict prompt
6. Ollama returns answer (constrained to document)
```

## Key Variables Explained

- `embeddings` - Converts text to 384-dimensional vectors
- `llm` - Ollama mistral model (7B parameters)
- `vectorstore` - Chroma database storing embeddings
- `chunks` - Text split into 500-char pieces
- `context` - Top 5 chunks combined for LLM
- `prompt` - Question + context + instructions for LLM

## Common Questions

**Q: Why is first answer slow?**
A: Ollama loads 4.3GB model into memory (10-30 sec). Later answers are fast (2-5 sec).

**Q: Why is answer still vague?**
A: Your document might be vague. Use specific details, numbers, and structure.

**Q: Can I ask follow-up questions?**
A: Each question is independent. Provide context in each question.

**Q: Can I upload multiple documents?**
A: Yes! They're all indexed into same Chroma database.

**Q: Can I delete a document?**
A: Currently no delete feature. Clear `chroma_db/` folder to reset all.

## Files Modified

| File | Change | Why |
|------|--------|-----|
| **rag_system.py** | Rewrote query_rules() with explicit prompt | Better answers |
|  | Added k=5 (was k=3) | More context |
|  | Added line comments | Learn RAG |
| **app.py** | Added /api/chat endpoint | Fix missing route |
|  | Added line comments | Learn Flask |

## Files to Read for Learning

1. **rag_system.py** - Comments explain vector embeddings and LLM prompting
2. **app.py** - Comments explain Flask routing and REST APIs
3. **IMPROVEMENTS.md** - Detailed technical explanation
4. **templates/chatbot.html** - How frontend calls the API

## Next Steps

1. Run the app (follow "Run It Now" section)
2. Test with a simple TXT document
3. Ask specific questions (not vague ones)
4. Read the code comments to understand
5. Experiment with different document structures

---

**Pro Tips:**
- More specific questions = better answers
- Better structured documents = better answers
- First query slow (10-30s), later queries fast (2-5s)
- Each query is independent - be specific
