# Rendered Output Files

## Overview
The backend automatically generates fully-rendered HTML output files for all lessons and sessions. These files contain complete animations, styles, and interactive controls.

## Automatic Generation

### When Files Are Created

1. **Lesson Generation** (`POST /generate`):
   - When a new lesson is generated, a rendered HTML file is automatically created
   - Saved to: `backend/data/rendered/lesson_{lesson_id}.html`

2. **Session Creation** (`POST /sessions`):
   - When a session is created with a `lesson_id`, a rendered HTML file is automatically created
   - Saved to: `backend/data/rendered/session_{session_id}.html`

3. **Session Update** (`PUT /sessions/{session_id}`):
   - When a session is updated with a `lesson_id`, the rendered file is automatically updated

## File Locations

- **Lessons**: `backend/data/rendered/lesson_{lesson_id}.html`
- **Sessions**: `backend/data/rendered/session_{session_id}.html`

## API Endpoints

### 1. Get Rendered Lesson
```http
GET /render/{lesson_id}
```
Returns full HTML page with animations for a lesson.

### 2. Get Embeddable Lesson
```http
GET /render/{lesson_id}/embed
```
Returns embeddable HTML content (body + styles + scripts) for React integration.

### 3. Get Rendered Session
```http
GET /sessions/{session_id}/render
```
Returns full HTML page with animations for a session's lesson.

### 4. Get Embeddable Session
```http
GET /sessions/{session_id}/render/embed
```
Returns embeddable HTML content for a session's lesson.

### 5. List All Rendered Files
```http
GET /rendered
```
Returns a list of all rendered output files with metadata:
```json
{
  "rendered_files": [
    {
      "filename": "lesson_1f6f838b.html",
      "id": "1f6f838b",
      "type": "lesson",
      "size": 45678,
      "created": "2025-12-07T10:00:00",
      "modified": "2025-12-07T10:00:00",
      "url": "/rendered/lesson_1f6f838b.html",
      "render_url": "/render/1f6f838b"
    },
    {
      "filename": "session_4c8916d3.html",
      "id": "4c8916d3",
      "type": "session",
      "size": 45678,
      "created": "2025-12-07T11:00:00",
      "modified": "2025-12-07T11:00:00",
      "url": "/rendered/session_4c8916d3.html",
      "render_url": "/sessions/4c8916d3/render"
    }
  ],
  "count": 82
}
```

### 6. Get Specific Rendered File
```http
GET /rendered/{filename}
```
Returns a specific rendered HTML file by filename.

## Manual Generation

To generate rendered files for all existing lessons and sessions:

```bash
cd backend
python3 generate_all_rendered.py
```

This will:
- Generate HTML files for all lessons in `backend/data/lesson_*.json`
- Generate HTML files for all sessions in `backend/data/sessions/session_*.json`
- Save all files to `backend/data/rendered/`

## File Features

Each rendered HTML file includes:
- ✅ Full page with header and controls
- ✅ All step content with animations
- ✅ Key points with slide-in animations
- ✅ Formula boxes with scale animations
- ✅ SVG assets with fade, zoom, and path drawing animations
- ✅ Play/Pause/Next/Previous/Restart controls
- ✅ Progress bar
- ✅ Auto-play on load
- ✅ Responsive design

## Usage in Frontend

The frontend can access these rendered files via:

1. **Direct URL**: `http://localhost:8000/rendered/lesson_{lesson_id}.html`
2. **API Endpoint**: `http://localhost:8000/render/{lesson_id}`
3. **Embed Endpoint**: `http://localhost:8000/render/{lesson_id}/embed` (for React integration)

## Example

```bash
# Generate a lesson
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Teach me Ohm'\''s Law"}'

# Response includes lesson_id: "abc12345"

# Access rendered output
open http://localhost:8000/rendered/lesson_abc12345.html
# or
open http://localhost:8000/render/abc12345
```

## File Management

- Files are automatically created when lessons/sessions are generated
- Files are updated when sessions are updated
- Files can be manually regenerated using `generate_all_rendered.py`
- Files are stored in `backend/data/rendered/` directory

