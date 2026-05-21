# Setup Guide - Fix All Issues ✅

## Issue 1: app.py Error ✅ FIXED

Fixed the syntax error in line 181. app.py is now working!

## Issue 2: Missing Dependencies

You need to install: `sentence-transformers` and `chromadb`

```bash
pip3 install sentence-transformers chromadb langchain-huggingface
```

**This takes 5-10 minutes** (first time only). Let it run!

## Issue 3: Ollama Not Found

Use the full path instead of just `ollama`:

```bash
/Applications/Ollama.app/Contents/MacOS/Ollama serve
```

Or create an alias:
```bash
echo 'alias ollama="/Applications/Ollama.app/Contents/MacOS/Ollama"' >> ~/.zshrc
source ~/.zshrc
# Now you can use: ollama serve
```

## Issue 4: Ollama Shows Nothing in Terminal

**This is NORMAL!** ✅

When you run `ollama serve`, it:
- Starts the server on 127.0.0.1:11434
- Listens quietly for requests
- Shows nothing unless there's an error

**Don't close this terminal!** Let it run in background.

---

## Test It Now - Step by Step

### Step 1: Install Dependencies (5-10 minutes)
```bash
pip3 install sentence-transformers chromadb langchain-huggingface
```

Wait until you see: `Successfully installed ...`

### Step 2: Terminal 1 - Start Ollama (Keep Open!)
```bash
/Applications/Ollama.app/Contents/MacOS/Ollama serve
```

You should see:
```
time=... level=INFO msg="Listening on 127.0.0.1:11434"
```

**Leave this terminal open!**

### Step 3: Terminal 2 - Start Flask
```bash
cd "/Users/nabeel/Desktop/Python Learning/Society App"
python3 app.py
```

You should see:
```
Running on http://127.0.0.1:5050
```

### Step 4: Terminal 3 (or New Browser Tab)
Go to: **http://localhost:5050**

1. Login: `admin` / `admin123`
2. Click: "Management Documents"
3. Upload: Any TXT file with society rules
4. Logout
5. Login: `101` / `1234`  
6. Click: "Ask about Rules"
7. Ask: "What is the parking fee?"
8. Get answer from YOUR document! ✨

---

## Common Issues & Fixes

### Error: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solution:**
```bash
pip3 install sentence-transformers chromadb
```

Wait 5-10 minutes for download and installation.

### Error: "Connection refused" or "Ollama not responding"

**Solution:** Check Terminal 1 is running `ollama serve`

If not, start it:
```bash
/Applications/Ollama.app/Contents/MacOS/Ollama serve
```

### Error: "No relevant information found in documents"

**Solution:** You haven't uploaded a document yet!

1. Login as admin
2. Go to "Management Documents"
3. Upload a TXT file with rules
4. Then try asking again

### Error: "'ollama' command not found" in Flask app

**Solution:** Flask also needs Ollama to be running!

Make sure Terminal 1 has Ollama running before starting Flask.

---

## Installation Takes Long - Why?

The first time you install:
- `sentence-transformers`: ~500MB (machine learning model)
- `chromadb`: ~100MB (vector database)
- **Total: ~600MB**

This downloads and installs once. Next time will be instant!

**Don't interrupt pip install!** Let it finish.

---

## Three Terminal Strategy

Keep 3 terminals open:

| Terminal | Command | Status |
|----------|---------|--------|
| Terminal 1 | `ollama serve` | Keep open! |
| Terminal 2 | `python3 app.py` | Keep open! |
| Terminal 3 | Browser / Testing | Use for testing |

---

## Success Checklist ✅

- [ ] Dependencies installed (sentence-transformers, chromadb)
- [ ] Terminal 1: Ollama running (`ollama serve`)
- [ ] Terminal 2: Flask running (`python3 app.py`)
- [ ] Browser: http://localhost:5050 works
- [ ] Can login as admin/admin123
- [ ] Can upload TXT document
- [ ] Can logout and login as 101/1234
- [ ] Can ask questions in chatbot
- [ ] Get specific answers from YOUR document! 🎉

---

## Next Steps After Success

1. Read: **START_HERE.md**
2. Read: **README_FIXES.md**
3. Try uploading different documents
4. Read code comments to learn
5. Modify the RAG prompt to experiment

---

## You've Got This! 🚀

The hard part (fixing code) is done!

Now just:
1. Install dependencies (takes time but easy)
2. Run three commands (each in different terminal)
3. Test in browser
4. Enjoy your RAG chatbot!

Questions? Check the documentation files!
