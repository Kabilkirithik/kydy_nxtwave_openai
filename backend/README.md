# Kydy Lesson Generator Backend

FastAPI backend service that generates educational lessons with animated SVG primitives using Gemini LLM and Hugging Face StarVector.

## Setup

### Prerequisites

- Python 3.10+
- pip or poetry

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional, system works with fallbacks):
```bash
export GEMINI_API_KEY="your-gemini-api-key"
export HF_API_TOKEN="your-huggingface-token"
```

### Setting Up API Keys (Optional)

The system works without API keys using fallbacks, but for best results:

**Option 1: Interactive Python script**
```bash
cd backend
python setup_api_keys.py
```

**Option 2: Manual setup**
```bash
cd backend
cp .env.example .env
# Edit .env and add your keys
```

See `API_KEYS_SETUP.md` in the project root for detailed instructions.

### Running the Server

**Option 1: From project root directory**
```bash
# From the project root (parent of backend/)
uvicorn backend.app:app --reload
```

**Option 2: From backend directory**
```bash
# From inside the backend/ directory
cd backend
uvicorn app:app --reload
```

The server will start on `http://localhost:8000`

**New endpoints:**
- `GET /` - API information
- `GET /health` - Health check (shows API key status)

## API Endpoints

### POST /generate

Generate a lesson from a user prompt.

**Request:**
```json
{
  "prompt": "Teach me Ohm's Law with a resistor and battery"
}
```

**Response:**
```json
{
  "status": "ok",
  "lesson_id": "abc12345",
  "render_url": "/render/abc12345",
  "lesson": {
    "lesson_id": "abc12345",
    "topic": "Ohm's Law",
    "timeline": [...],
    ...
  }
}
```

### GET /lesson/{lesson_id}

Get the full lesson JSON by ID.

**Response:**
```json
{
  "lesson_id": "abc12345",
  "topic": "Ohm's Law",
  "timeline": [
    {
      "step_index": 0,
      "title": "Introduction",
      "description": "...",
      "duration_seconds": 30,
      "assets": [...]
    }
  ]
}
```

### GET /assets/{asset_name}

Serve generated SVG asset files.

### GET /render/{lesson_id}

HTML preview page for a lesson (useful for quick testing).

## Testing

Run tests with pytest:

```bash
pytest backend/tests/
```

## Example Usage

### Generate a lesson:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Teach me Ohm'\''s Law with a resistor and battery"}'
```

### Get lesson JSON:

```bash
curl "http://localhost:8000/lesson/abc12345"
```

### View lesson in browser:

Open `http://localhost:8000/render/abc12345` in your browser.

## Architecture

- **app.py**: Main FastAPI application with endpoints
- **gemini_client.py**: Gemini LLM client for extracting lesson structure
- **starvector_client.py**: Hugging Face StarVector client for SVG generation
- **fallbacks.py**: Parametric SVG generators (resistor, battery, stethoscope, graph)
- **data/primitives.json**: Cache of generated primitives
- **assets/**: Directory storing generated SVG files

## Fallback Behavior

The system is designed to work even without API keys:

- If `GEMINI_API_KEY` is missing, uses keyword-based fallback extraction
- If `HF_API_TOKEN` is missing or StarVector fails, uses parametric SVG generators
- All primitives are cached to avoid redundant generation

## Notes

- Lesson JSON files are saved to `backend/data/lesson_{id}.json`
- SVG assets are saved to `backend/assets/`
- Primitive cache uses SHA256 hashing for cache keys
- SVG content is sanitized to remove dangerous elements (scripts, foreignObject, etc.)

