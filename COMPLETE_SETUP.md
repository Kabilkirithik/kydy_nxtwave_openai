# Complete Setup Guide

This guide will walk you through setting up the entire Kydy system from scratch.

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ and npm installed
- (Optional) API keys for Gemini and Hugging Face

## Step 1: Backend Setup

### 1.1 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Set Up API Keys (Optional but Recommended)

**Option A: Interactive Script**
```bash
python setup_api_keys.py
```

**Option B: Manual**
```bash
cp .env.example .env
# Edit .env and add your keys
```

See `API_KEYS_SETUP.md` for detailed instructions on getting API keys.

### 1.3 Start Backend Server

```bash
# From backend directory
uvicorn app:app --reload
```

Or from project root:
```bash
uvicorn backend.app:app --reload
```

Backend will run on `http://localhost:8000`

### 1.4 Verify Backend

Open a new terminal and test:

```bash
# Check health
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","gemini_configured":true,"hf_configured":true}
```

## Step 2: Frontend Setup

### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

### 2.2 Configure API Base URL

Create `frontend/.env`:

```env
VITE_API_BASE=http://localhost:8000
```

### 2.3 Start Frontend Server

```bash
npm run dev
```

Frontend will run on `http://localhost:8080`

## Step 3: Test the Integration

### 3.1 Generate a Lesson

1. Open `http://localhost:8080/generate` in your browser
2. Enter a prompt: "Teach me Ohm's Law with a resistor and battery"
3. Click "Generate Lesson"
4. Wait for generation (may take 10-30 seconds)
5. Click "View Lesson"

### 3.2 View the Lesson

- The lesson should load automatically
- SVG animations should play
- Use controls to play/pause/seek

### 3.3 Test via API

```bash
# Generate a lesson
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Teach me circuits"}'

# Copy the lesson_id from response, then:
curl "http://localhost:8000/lesson/{lesson_id}"
```

## Step 4: Get Your API Keys

### Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key
5. Run: `python backend/setup_api_keys.py` and paste it

### Hugging Face Token

1. Visit: https://huggingface.co/settings/tokens
2. Sign in/up
3. Click "New token"
4. Name it "kydy-starvector"
5. Select "Read" permission
6. Copy the token
7. Run: `python backend/setup_api_keys.py` and paste it

## Troubleshooting

### Backend won't start

- Check Python version: `python --version` (needs 3.10+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is free: `lsof -i :8000`

### Frontend can't connect

- Verify backend is running: `curl http://localhost:8000/health`
- Check `.env` file has `VITE_API_BASE=http://localhost:8000`
- Restart frontend after changing `.env`
- Check browser console for CORS errors

### Lessons not generating

- Check backend logs for errors
- Verify API keys in `/health` endpoint
- System works with fallbacks even without keys
- Check `backend/data/` and `backend/assets/` directories exist

### Animations not working

- Check browser console for errors
- Verify anime.js loads (check Network tab)
- Try refreshing the page
- Check that SVG assets are loading

## Quick Start (Minimal)

If you just want to test quickly without API keys:

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

Then:
1. Open `http://localhost:8080/generate`
2. Enter any prompt
3. Generate and view lesson

The system will use fallbacks and still work!

## Next Steps

- Read `INTEGRATION_GUIDE.md` for architecture details
- Read `API_KEYS_SETUP.md` for API key setup
- Read `QUICKSTART.md` for quick reference
- Customize the renderer in `frontend/src/renderer.js`
- Add more primitives in `backend/fallbacks.py`

## File Structure

```
.
├── backend/
│   ├── app.py              # Main FastAPI app
│   ├── gemini_client.py     # Gemini LLM client
│   ├── starvector_client.py # Hugging Face client
│   ├── fallbacks.py         # Parametric SVG generators
│   ├── data/                # Lesson JSON files
│   ├── assets/              # Generated SVG files
│   └── tests/               # Pytest tests
├── frontend/
│   ├── src/
│   │   ├── renderer.js      # Core renderer
│   │   ├── pages/
│   │   │   ├── GenerateLessonPage.tsx
│   │   │   └── LessonRendererPage.tsx
│   │   └── App.tsx          # Routes
│   └── renderer-demo.html  # Standalone demo
└── Documentation files
```

## Support

- Check logs in backend terminal
- Check browser console (F12)
- Review `INTEGRATION_GUIDE.md` for detailed flow
- System works with fallbacks - test without API keys first!

