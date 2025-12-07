# Frontend-Backend Integration Guide

This guide explains how the frontend and backend are integrated and how to use them together.

## Architecture Overview

```
Frontend (React/TypeScript)          Backend (FastAPI)
     │                                    │
     ├─ GenerateLessonPage ──────────────┼─ POST /generate
     │                                    │
     ├─ LessonRendererPage ──────────────┼─ GET /lesson/{id}
     │                                    │
     └─ Renderer (renderer.js) ──────────┼─ GET /assets/{name}
                                          │
                                          └─ GET /render/{id}
```

## Complete Integration Flow

### 1. Generate a Lesson (Frontend → Backend)

**Frontend**: `GenerateLessonPage.tsx`
- User enters a prompt
- Frontend calls `POST /generate` with `{ "prompt": "..." }`
- Backend processes and returns lesson JSON with `lesson_id`
- Frontend redirects to `/renderer?id={lesson_id}`

**Backend**: `app.py` → `/generate` endpoint
- Extracts lesson structure using Gemini (or fallback)
- Generates SVG primitives using StarVector (or fallback)
- Saves lesson to `backend/data/lesson_{id}.json`
- Saves assets to `backend/assets/`
- Returns lesson JSON

### 2. View a Lesson (Frontend → Backend)

**Frontend**: `LessonRendererPage.tsx` + `renderer.js`
- Loads lesson JSON from `GET /lesson/{id}`
- For each asset, loads SVG from `GET /assets/{name}` or uses inline SVG
- Animates SVG primitives step-by-step
- Provides play/pause/seek controls

**Backend**: `app.py` → `/lesson/{id}` and `/assets/{name}` endpoints
- Serves lesson JSON from `backend/data/`
- Serves SVG files from `backend/assets/`

## API Endpoints

### Backend Endpoints

| Endpoint | Method | Description | Frontend Usage |
|----------|--------|-------------|----------------|
| `/` | GET | API info | Health check |
| `/health` | GET | Health status | Check API keys |
| `/generate` | POST | Generate lesson | `GenerateLessonPage` |
| `/lesson/{id}` | GET | Get lesson JSON | `LessonRendererPage` |
| `/assets/{name}` | GET | Get SVG asset | `renderer.js` |
| `/render/{id}` | GET | HTML preview | Direct browser access |

### Frontend Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Index` | Landing page |
| `/generate` | `GenerateLessonPage` | Generate new lessons |
| `/renderer` | `LessonRendererPage` | View and play lessons |

## Configuration

### Backend Configuration

**Environment Variables** (in `backend/.env`):
```env
GEMINI_API_KEY=your-key
HF_API_TOKEN=your-token
```

**CORS Settings** (in `backend/app.py`):
```python
allow_origins=["http://localhost:8080", "http://localhost:5173"]
```

### Frontend Configuration

**Environment Variables** (in `frontend/.env`):
```env
VITE_API_BASE=http://localhost:8000
```

**Renderer Configuration** (in `renderer.js`):
```javascript
this.apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
```

## Running the Full Stack

### Terminal 1: Backend
```bash
cd backend
uvicorn app:app --reload
```
Backend runs on `http://localhost:8000`

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:8080`

## Testing the Integration

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Generate a Lesson (via Frontend)
1. Open `http://localhost:8080/generate`
2. Enter a prompt: "Teach me Ohm's Law with a resistor and battery"
3. Click "Generate Lesson"
4. Wait for generation to complete
5. Click "View Lesson"

### 3. View the Lesson
- Lesson should load automatically
- SVG animations should play
- Controls should work (play/pause/seek)

### 4. Test via API Directly
```bash
# Generate
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Teach me circuits"}'

# Get lesson (use lesson_id from response)
curl "http://localhost:8000/lesson/abc12345"
```

## Data Flow

### Lesson Generation Flow

```
User Input (Frontend)
    ↓
POST /generate { "prompt": "..." }
    ↓
Backend: Gemini extracts structure
    ↓
Backend: StarVector generates SVGs (or fallback)
    ↓
Backend: Saves lesson + assets
    ↓
Response: { lesson_id, lesson: {...} }
    ↓
Frontend: Redirects to /renderer?id={lesson_id}
```

### Lesson Rendering Flow

```
Frontend: GET /lesson/{id}
    ↓
Backend: Returns lesson JSON
    ↓
Frontend: For each asset in timeline
    ↓
    ├─ If inline SVG: Use directly
    └─ If URL: GET /assets/{name}
    ↓
Frontend: Render SVG in container
    ↓
Frontend: Animate (fade, zoom, path drawing)
    ↓
User: Interacts with controls
```

## Troubleshooting

### Frontend can't connect to backend

1. **Check backend is running**: `curl http://localhost:8000/health`
2. **Check CORS settings**: Backend must allow frontend origin
3. **Check API base URL**: Frontend `.env` must have correct `VITE_API_BASE`
4. **Check browser console**: Look for CORS or network errors

### Lessons not generating

1. **Check backend logs**: Look for errors in terminal
2. **Check API keys**: Verify in `/health` endpoint
3. **Check file permissions**: `backend/data/` and `backend/assets/` must be writable
4. **Check network**: Backend needs internet for API calls (or uses fallbacks)

### Animations not working

1. **Check anime.js**: Should load from CDN automatically
2. **Check browser console**: Look for JavaScript errors
3. **Check SVG format**: Assets must be valid SVG
4. **Check renderer init**: Verify `#lesson-root` element exists

### Assets not loading

1. **Check asset URLs**: Should be `/assets/{name}`
2. **Check backend serves assets**: Test `curl http://localhost:8000/assets/resistor_abc123.svg`
3. **Check CORS**: Asset requests need CORS headers
4. **Check file exists**: Verify file in `backend/assets/` directory

## Next Steps

- Add authentication for protected endpoints
- Add lesson library/persistence
- Add user accounts and lesson history
- Add real-time collaboration
- Add more primitive types
- Enhance animations

