# Backend-Frontend Integration Summary

## Overview
The system now supports **backend-rendered animations** that can be embedded directly into the frontend, providing a seamless integration between backend rendering and frontend display.

## Backend Endpoints

### 1. `GET /render/{lesson_id}`
- **Purpose**: Full HTML page with animations
- **Returns**: Complete HTML document with all styles and scripts
- **Use Case**: Standalone preview page
- **Example**: `http://localhost:8000/render/1f6f838b`

### 2. `GET /render/{lesson_id}/embed`
- **Purpose**: Embeddable HTML content (body only)
- **Returns**: Just the body content without `<html>`, `<head>`, `<body>` tags
- **Use Case**: Embedding into React components
- **Example**: `http://localhost:8000/render/1f6f838b/embed`

### 3. `GET /lesson/{lesson_id}`
- **Purpose**: Lesson JSON data
- **Returns**: JSON with timeline, assets, key_points, formulas
- **Use Case**: Client-side rendering
- **Example**: `http://localhost:8000/lesson/1f6f838b`

## Frontend Integration

### Option 1: Backend-Rendered HTML (Recommended)
Set `VITE_USE_BACKEND_RENDER=true` in your `.env` file:

```env
VITE_USE_BACKEND_RENDER=true
VITE_API_BASE=http://localhost:8000
```

The frontend will:
1. Fetch HTML from `/render/{lesson_id}/embed`
2. Inject it directly into the DOM
3. Auto-start animations

### Option 2: Client-Side Rendering (Default)
If `VITE_USE_BACKEND_RENDER` is not set or `false`:
1. Fetches JSON from `/lesson/{lesson_id}`
2. Uses `KydyRenderer` class to render client-side
3. Animates using anime.js

## Format Compatibility

### Backend Rendered HTML Format:
```html
<div class="header">...</div>
<div class="controls">...</div>
<div id="lesson-timeline">
  <div class="step-container active">
    <div class="step-title">...</div>
    <div class="step-description">...</div>
    <div class="key-points">...</div>
    <div class="formula-box">...</div>
    <div class="asset-container">
      <svg>...</svg>
    </div>
  </div>
</div>
```

### Frontend Container:
```tsx
<div 
  id="lesson-content-root" 
  ref={lessonRootRef} 
  className="h-full w-full overflow-auto p-4"
>
  {/* Backend-rendered HTML injected here */}
</div>
```

## Animation Features

Both rendering methods support:
- ✅ SVG fade-in and zoom animations
- ✅ Path drawing animations
- ✅ Text box animations
- ✅ Key points slide-in animations
- ✅ Formula scale animations
- ✅ Play/Pause/Next/Previous controls
- ✅ Progress bar
- ✅ Auto-play on load

## Testing

1. **Test Backend Rendering**:
   ```bash
   # Generate a lesson
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Teach me Ohm'\''s Law"}'
   
   # View rendered HTML
   open http://localhost:8000/render/{lesson_id}
   ```

2. **Test Frontend Integration**:
   - Set `VITE_USE_BACKEND_RENDER=true` in `.env`
   - Start frontend: `npm run dev`
   - Navigate to a session page
   - Backend-rendered HTML will be injected

## Benefits of Backend Rendering

1. **Consistent Output**: Same animations across all clients
2. **Server-Side Processing**: Heavy rendering done on server
3. **SEO Friendly**: Full HTML content for search engines
4. **Performance**: Pre-rendered content loads faster
5. **Offline Preview**: Can save HTML files for offline viewing

## Fallback Behavior

If backend rendering fails, the frontend automatically falls back to client-side rendering, ensuring the lesson always displays.

