# Quick Start Guide

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- (Optional) GEMINI_API_KEY and HF_API_TOKEN for full functionality

## Setup Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Set environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export HF_API_TOKEN="your-huggingface-token"

# Start the backend server
# Option 1: From project root
uvicorn backend.app:app --reload

# Option 2: From backend directory
cd backend
uvicorn app:app --reload
```

Backend will run on `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# (Optional) Create .env file
echo "VITE_API_BASE=http://localhost:8000" > .env

# Start the frontend dev server
npm run dev
```

Frontend will run on `http://localhost:8080`

## Testing the System

### Step 1: Generate a Lesson

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Teach me Ohm'\''s Law with a resistor and battery"}'
```

Copy the `lesson_id` from the response (e.g., `"lesson_id": "abc12345"`)

### Step 2: View the Lesson

**Option A: React App**
- Open `http://localhost:8080/renderer?id=<lesson_id>`
- The lesson will load and play automatically

**Option B: Backend Preview**
- Open `http://localhost:8000/render/<lesson_id>`
- Simple HTML preview page

**Option C: Standalone Demo**
- Open `frontend/renderer-demo.html` in browser
- Enter the lesson ID and click "Load Lesson"

## Example Workflow

1. Start backend: `uvicorn backend.app:app --reload`
2. Start frontend: `npm run dev` (in frontend directory)
3. Generate lesson:
   ```bash
   curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Explain how a battery powers a circuit"}'
   ```
4. Copy `lesson_id` from response
5. Open `http://localhost:8080/renderer?id=<lesson_id>`
6. Watch the animated lesson play!

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.10+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is not in use

### Frontend can't connect to backend
- Verify backend is running on `http://localhost:8000`
- Check `.env` file has `VITE_API_BASE=http://localhost:8000`
- Restart frontend dev server after changing `.env`

### No animations
- Check browser console for errors
- Verify anime.js is loading (check Network tab)
- Try refreshing the page

### Lessons not generating
- System works without API keys (uses fallbacks)
- Check backend logs for errors
- Verify `backend/data/` and `backend/assets/` directories exist

## File Locations

- **Backend lessons**: `backend/data/lesson_{id}.json`
- **Backend assets**: `backend/assets/{primitive}_{id}.svg`
- **Primitive cache**: `backend/data/primitives.json`

## Next Steps

- Read `IMPLEMENTATION_SUMMARY.md` for architecture details
- Read `backend/README.md` for API documentation
- Read `frontend/README.md` for renderer API

