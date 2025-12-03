# Diabetes Agentic RAG Chatbot

A production-ready diabetes chatbot with **admin-trained RAG**, **general health LLM fallback**, **per-user persistent memory**, and **image support**.

## Features

✅ **Admin-Trained RAG** - Only answers from your curated diabetes knowledge base  
✅ **Safety-First** - Emergency detection & medication change blocking  
✅ **Persistent Memory** - Per-user profile and conversation history  
✅ **Image Support** - Analyze medical images using BLIP captioning + LLM  
✅ **Agentic Flow** - Automatic routing between RAG and general health responses  
✅ **Free & Open Source** - Uses Groq LLM + HuggingFace models

## Project Structure

```
diabetes_agent/
├── backend/
│   ├── app.py                 # FastAPI server
│   ├── config.py              # Configuration & prompts
│   ├── nodes.py               # Agent nodes (RAG, LLM, image)
│   ├── graphs.py              # GraphState & routing logic
│   ├── rag/
│   │   ├── embedder.py        # HuggingFace embeddings
│   │   ├── vectorstore.py     # Chroma vector DB
│   │   └── safety.py          # Emergency & med safety
│   ├── memory/
│   │   └── store.py           # JSON-based user memory
│   ├── vision/
│   │   └── image_caption.py   # BLIP image captioning
│   └── data/
│       ├── raw_admin/         # Your diabetes .txt files
│       └── chroma_admin/      # Chroma DB (auto-generated)
├── scripts/
│   └── prepare_admin_kb.py    # Build knowledge base
├── requirements.txt
└── .env
```

## Installation

### 1. Create Virtual Environment

```bash
cd diabetes_agent
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** `torch` is large (~2GB). Installation may take a few minutes.

### 3. Configure Environment

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key from: https://console.groq.com/

### 4. Add Your Diabetes Knowledge

1. Put your cleaned diabetes education `.txt` files in `backend/data/raw_admin/`
2. Build the knowledge base:

```bash
python scripts/prepare_admin_kb.py
```

This creates embeddings in `backend/data/chroma_admin/`

## Running the Server

```bash
cd diabetes_agent
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Server will run at: **http://localhost:8000**

API docs available at: **http://localhost:8000/docs**

## API Endpoints

### 1. Text Chat

**POST** `/chat`

```json
{
  "user_id": "user123",
  "message": "What does my high risk score mean?",
  "profile": {
    "age": 22,
    "bmi": 28.5,
    "hba1c": 7.8,
    "risk_score": 0.84
  }
}
```

**Response:**

```json
{
  "answer": "Your risk score of 0.84 indicates...",
  "route_reason": "admin_rag",
  "intent": "admin_rag"
}
```

### 2. Image Chat

**POST** `/chat-with-image`

Form data:
- `user_id`: string
- `message`: string (optional)
- `profile_json`: JSON string (optional)
- `image`: file upload

### 3. Health Check

**GET** `/health`

Returns: `{"status": "ok"}`

## Integration with Your Website

### JavaScript/React Example

```javascript
// Text chat
const response = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    user_id: currentUser.id,
    message: userQuestion,
    profile: {
      age: currentUser.age,
      bmi: currentUser.bmi,
      risk_score: currentUser.last_prediction?.risk_score
    }
  })
});

const data = await response.json();
console.log(data.answer);

// Image chat
const formData = new FormData();
formData.append("user_id", currentUser.id);
formData.append("message", "Is this concerning for diabetes?");
formData.append("profile_json", JSON.stringify({ age: 22, risk_score: 0.84 }));
formData.append("image", fileInput.files[0]);

const imageResponse = await fetch("http://localhost:8000/chat-with-image", {
  method: "POST",
  body: formData
});

const imageData = await imageResponse.json();
console.log(imageData.answer);
```

## How It Works

### 1. Safety Layer
- Detects emergency keywords → directs to seek urgent care
- Blocks medication change requests → tells user to consult doctor

### 2. Intent Classification
- **admin_rag**: Diabetes-specific questions use your knowledge base
- **general_health**: Other health topics use LLM (still safe, no diagnosis)

### 3. Agent Flow

```
User Message
    ↓
Safety Checks (emergency, meds)
    ↓
Image Analysis (if image provided)
    ↓
Load User Memory (profile + history)
    ↓
Classify Intent (diabetes → RAG, other → LLM)
    ↓
Generate Answer
    ↓
Add Disclaimer
    ↓
Save to Memory
```

### 4. Memory System
- **Profile**: Persistent user data (age, BMI, HbA1c, risk score)
- **History**: Last 30 conversation turns per user
- Stored in `backend/memory_store.json`

### 5. Image Analysis
- Uses Salesforce BLIP model (free, runs on CPU)
- Generates image caption → passes to LLM for context
- Still follows all safety rules (no diagnosis)

## Configuration

Edit `backend/config.py` to customize:

- **Prompts**: System prompts for RAG vs general health
- **Safety keywords**: Emergency detection patterns
- **Model settings**: Groq model, temperature, max tokens
- **Memory limits**: History length, RAG top-k results

## Production Deployment

### 1. Use Environment Variables

```bash
export GROQ_API_KEY=your_key
```

### 2. Use Production Server

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Add Authentication

Add JWT or API key validation in `app.py`:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "your_secret_key":
        raise HTTPException(status_code=401, detail="Invalid API key")
```

### 4. Database Storage

Replace JSON memory with PostgreSQL/MongoDB for production:

```python
# In memory/store.py, replace _load_all() and _save_all()
# with database queries
```

### 5. Image Cleanup

Add cron job to delete old images:

```bash
# Clean images older than 7 days
find tmp_images/ -type f -mtime +7 -delete
```

## Troubleshooting

### "No .txt files found"
→ Add your diabetes knowledge `.txt` files to `backend/data/raw_admin/`

### "GROQ_API_KEY not set"
→ Create `.env` file with your Groq API key

### "Module not found"
→ Make sure you're in the virtual environment: `venv\Scripts\activate`

### Slow image processing
→ BLIP runs on CPU by default. For faster processing, install CUDA-enabled PyTorch

### Import errors
→ Make sure you're running from the `diabetes_agent/` directory

## License

MIT License - Free for personal and commercial use

## Support

For issues or questions, check the API docs at `/docs` or review the code comments.

---

**Built with ❤️ for diabetes education and patient empowerment**
