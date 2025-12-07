"""
FastAPI backend for lesson generation with SVG primitives.
"""
import os
import json
import hashlib
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request as StarletteRequest
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from gemini_client import GeminiClient
from starvector_client import StarVectorClient
from fallbacks import ParametricSVGGenerator

app = FastAPI(title="Kydy Lesson Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

gemini_client = GeminiClient()
starvector_client = StarVectorClient()
fallback_generator = ParametricSVGGenerator()

PRIMITIVES_CACHE_FILE = DATA_DIR / "primitives.json"
if PRIMITIVES_CACHE_FILE.exists():
    with open(PRIMITIVES_CACHE_FILE, "r") as f:
        PRIMITIVES_CACHE = json.load(f)
else:
    PRIMITIVES_CACHE = {}
    with open(PRIMITIVES_CACHE_FILE, "w") as f:
        json.dump({}, f)


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    status: str
    lesson_id: str
    render_url: str
    lesson: Dict[str, Any]


class SessionData(BaseModel):
    session_id: str
    topic: str
    lesson_id: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []
    session_time: int = 0
    created_at: str
    updated_at: str


class SaveSessionRequest(BaseModel):
    topic: str
    lesson_id: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []
    session_time: int = 0


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Kydy Lesson Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "POST /generate",
            "get_lesson": "GET /lesson/{lesson_id}",
            "get_asset": "GET /assets/{asset_name}",
            "render": "GET /render/{lesson_id}",
            "render_embed": "GET /render/{lesson_id}/embed",
            "render_session": "GET /sessions/{session_id}/render",
            "render_session_embed": "GET /sessions/{session_id}/render/embed",
            "list_rendered": "GET /rendered",
            "get_rendered": "GET /rendered/{filename}",
            "health": "GET /health"
        },
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "hf_configured": bool(os.getenv("HF_API_TOKEN"))
    }


def compute_cache_key(primitive_id: str, params: Dict[str, Any], model_version: str = "v1") -> str:
    """Compute cache key from primitive_id, params, and model version."""
    canonical = json.dumps(params, sort_keys=True)
    raw = f"{primitive_id}:{canonical}:{model_version}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_or_generate_primitive(primitive_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get primitive from cache or generate new one.
    Returns dict with: asset_id, url, svg (inline), render_meta
    """
    cache_key = compute_cache_key(primitive_id, params)
    
    if cache_key in PRIMITIVES_CACHE:
        cached = PRIMITIVES_CACHE[cache_key]
        asset_file = cached.get("asset_file")
        if asset_file and (ASSETS_DIR / asset_file).exists():
            with open(ASSETS_DIR / asset_file, "r") as f:
                svg_content = f.read()
            return {
                "asset_id": cached["asset_id"],
                "primitive_id": primitive_id,
                "url": f"/assets/{asset_file}",
                "svg": svg_content if len(svg_content) < 5000 else None,  # Only inline small SVGs
                "render_meta": cached.get("render_meta", {})
            }
    
    svg_content = None
    asset_file = None
    
    try:
        prompt = f"Generate an SVG illustration of {primitive_id}"
        if params:
            prompt += f" with parameters: {json.dumps(params)}"
        svg_content = starvector_client.generate_svg(prompt)
    except Exception as e:
        print(f"StarVector generation failed: {e}")
    
    if not svg_content or not starvector_client.is_valid_svg(svg_content):
        print(f"Using parametric fallback for {primitive_id}")
        svg_content = fallback_generator.generate(primitive_id, params)
    
    asset_id = str(uuid.uuid4())[:8]
    asset_file = f"{primitive_id}_{asset_id}.svg"
    asset_path = ASSETS_DIR / asset_file
    
    with open(asset_path, "w") as f:
        f.write(svg_content)
    
    width, height = starvector_client.extract_dimensions(svg_content)
    render_meta = {
        "confidence": 0.8 if svg_content else 0.5,
        "width": width,
        "height": height
    }
    
    PRIMITIVES_CACHE[cache_key] = {
        "asset_id": asset_id,
        "asset_file": asset_file,
        "primitive_id": primitive_id,
        "params": params,
        "render_meta": render_meta
    }
    
    with open(PRIMITIVES_CACHE_FILE, "w") as f:
        json.dump(PRIMITIVES_CACHE, f, indent=2)
    
    return {
        "asset_id": asset_id,
        "primitive_id": primitive_id,
        "url": f"/assets/{asset_file}",
        "svg": svg_content if len(svg_content) < 5000 else None,
        "render_meta": render_meta
    }


def extract_lesson_structure(prompt: str) -> Dict[str, Any]:
    """Extract lesson structure from prompt using Gemini or fallback."""
    try:
        return gemini_client.extract_lesson_structure(prompt)
    except Exception as e:
        print(f"Gemini extraction failed: {e}, using fallback")
        prompt_lower = prompt.lower()
        
        if "ohm" in prompt_lower or "resistor" in prompt_lower:
            steps = [
                {
                    "title": "Introduction to Ohm's Law",
                    "description": "Ohm's Law is a fundamental principle in electrical engineering that describes the relationship between voltage, current, and resistance in an electrical circuit. It states that the current through a conductor between two points is directly proportional to the voltage across the two points and inversely proportional to the resistance between them.",
                    "key_points": [
                        "Ohm's Law: V = I × R",
                        "Voltage (V) is measured in volts",
                        "Current (I) is measured in amperes",
                        "Resistance (R) is measured in ohms"
                    ],
                    "formula": "V = I × R",
                    "duration_seconds": 20
                },
                {
                    "title": "Understanding Resistance",
                    "description": "Resistance is the opposition to the flow of electric current. In a resistor, resistance is determined by the material, length, and cross-sectional area. Color-coded bands on resistors indicate their resistance value, making it easy to identify components in circuits.",
                    "key_points": [
                        "Resistance opposes current flow",
                        "Measured in ohms (Ω)",
                        "Color bands indicate resistance value",
                        "Higher resistance = less current flow"
                    ],
                    "duration_seconds": 20
                },
                {
                    "title": "Circuit Analysis",
                    "description": "When analyzing circuits with Ohm's Law, we can calculate any one of the three variables (voltage, current, or resistance) if we know the other two. This makes circuit design and troubleshooting much easier. Let's see how voltage, current, and resistance interact in a simple circuit.",
                    "key_points": [
                        "Calculate voltage: V = I × R",
                        "Calculate current: I = V / R",
                        "Calculate resistance: R = V / I",
                        "All three are interconnected"
                    ],
                    "formula": "I = V / R",
                    "duration_seconds": 25
                }
            ]
            primitives = [
                {"primitive_id": "resistor", "params": {"value": "10kΩ"}},
                {"primitive_id": "battery", "params": {"voltage": "9V"}},
                {"primitive_id": "graph", "params": {}}
            ]
        else:
            steps = [
                {
                    "title": "Introduction",
                    "description": f"Welcome to this lesson about {prompt[:60]}. We'll explore the fundamental concepts and build a solid understanding step by step. This topic is important because it forms the foundation for deeper learning.",
                    "key_points": [
                        "Understanding the basics",
                        "Key terminology",
                        "Real-world applications",
                        "Why this matters"
                    ],
                    "duration_seconds": 20
                },
                {
                    "title": "Core Concepts",
                    "description": "Let's dive into the core concepts. We'll break down complex ideas into manageable pieces, using visual aids and examples to make everything clear. Each concept builds on the previous one, creating a comprehensive understanding.",
                    "key_points": [
                        "Breaking down complex ideas",
                        "Visual learning aids",
                        "Step-by-step progression",
                        "Building understanding"
                    ],
                    "duration_seconds": 25
                },
                {
                    "title": "Practical Application",
                    "description": "Now that we understand the theory, let's see how these concepts apply in real-world scenarios. Practical examples help solidify our understanding and show the relevance of what we've learned.",
                    "key_points": [
                        "Real-world examples",
                        "Practical applications",
                        "Connecting theory to practice",
                        "Hands-on learning"
                    ],
                    "duration_seconds": 25
                }
            ]
            primitives = [
                {"primitive_id": "graph", "params": {}},
                {"primitive_id": "graph", "params": {"points": [20, 40, 30, 50, 45, 60], "title": "Progress Over Time"}}
            ]
        
        return {
            "topic": prompt[:60] if len(prompt) > 60 else prompt,
            "subtopic": "Introduction",
            "intent": "educational",
            "audience": "beginner",
            "suggested_steps": steps,
            "primitives": primitives,
            "learning_objectives": ["Understand the core concepts", "Apply knowledge practically", "Build a solid foundation"]
        }


@app.post("/generate", response_model=GenerateResponse)
async def generate_lesson(request: GenerateRequest):
    """Generate a lesson from a user prompt."""
    try:
        lesson_structure = extract_lesson_structure(request.prompt)
        
        lesson_id = str(uuid.uuid4())[:8]
        
        timeline = []
        all_primitives = lesson_structure.get("primitives", [])
        steps = lesson_structure.get("suggested_steps", [])
        
        if not all_primitives:
            prompt_lower = request.prompt.lower()
            if "resistor" in prompt_lower or "ohm" in prompt_lower or "circuit" in prompt_lower:
                all_primitives = [
                    {"primitive_id": "resistor", "params": {}},
                    {"primitive_id": "battery", "params": {}},
                    {"primitive_id": "graph", "params": {}}
                ]
            elif "medical" in prompt_lower or "stethoscope" in prompt_lower:
                all_primitives = [
                    {"primitive_id": "stethoscope", "params": {}},
                    {"primitive_id": "graph", "params": {}}
                ]
            else:
                all_primitives = [
                    {"primitive_id": "graph", "params": {}},
                    {"primitive_id": "graph", "params": {"points": [20, 40, 30, 50, 45, 60]}}
                ]
        
        for step_idx, step in enumerate(steps):
            step_assets = []
            
            if all_primitives:
                primitives_per_step = max(1, len(all_primitives) // len(steps))
                start_idx = step_idx * primitives_per_step
                end_idx = min(start_idx + primitives_per_step, len(all_primitives))
                
                if step_idx == len(steps) - 1:
                    end_idx = len(all_primitives)
                
                step_primitives = all_primitives[start_idx:end_idx]
                
                if not step_primitives and step_idx < len(all_primitives):
                    step_primitives = [all_primitives[step_idx % len(all_primitives)]]
            
            for primitive_spec in step_primitives:
                primitive_id = primitive_spec.get("primitive_id", "graph")
                params = primitive_spec.get("params", {})
                asset_data = get_or_generate_primitive(primitive_id, params)
                step_assets.append(asset_data)
            
            duration = max(15, step.get("duration_seconds", 15))
            
            timeline.append({
                "step_index": step_idx,
                "title": step.get("title", f"Step {step_idx + 1}"),
                "description": step.get("description", ""),
                "key_points": step.get("key_points", []),
                "formula": step.get("formula", ""),
                "duration_seconds": duration,
                "assets": step_assets
            })
        
        lesson_json = {
            "lesson_id": lesson_id,
            "topic": lesson_structure.get("topic", "General Lesson"),
            "subtopic": lesson_structure.get("subtopic", ""),
            "intent": lesson_structure.get("intent", "educational"),
            "audience": lesson_structure.get("audience", "beginner"),
            "learning_objectives": lesson_structure.get("learning_objectives", []),
            "timeline": timeline
        }
        
        lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
        with open(lesson_file, "w") as f:
            json.dump(lesson_json, f, indent=2)
        
        try:
            rendered_html = generate_rendered_html(lesson_json, "")
            rendered_output_dir = DATA_DIR / "rendered"
            rendered_output_dir.mkdir(exist_ok=True)
            rendered_output_file = rendered_output_dir / f"lesson_{lesson_id}.html"
            with open(rendered_output_file, "w", encoding="utf-8") as f:
                f.write(rendered_html)
            print(f"✅ Generated rendered output: {rendered_output_file}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to generate rendered output: {e}")
        
        return GenerateResponse(
            status="ok",
            lesson_id=lesson_id,
            render_url=f"/render/{lesson_id}",
            lesson=lesson_json
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/lesson/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get lesson JSON by ID."""
    lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
    if not lesson_file.exists():
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    with open(lesson_file, "r") as f:
        return json.load(f)


@app.get("/assets/{asset_name}")
async def get_asset(asset_name: str):
    """Serve SVG asset file."""
    asset_path = ASSETS_DIR / asset_name
    if not asset_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return FileResponse(
        asset_path,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=3600"}
    )


SESSIONS_DIR = DATA_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


@app.post("/sessions")
async def save_session(request: SaveSessionRequest):
    """Save a session."""
    try:
        session_id = str(uuid.uuid4())[:8]
        created_at = datetime.datetime.now().isoformat()
        updated_at = created_at
        
        session_data = {
            "session_id": session_id,
            "topic": request.topic,
            "lesson_id": request.lesson_id,
            "messages": request.messages,
            "notes": request.notes,
            "session_time": request.session_time,
            "created_at": created_at,
            "updated_at": updated_at
        }
        
        session_file = SESSIONS_DIR / f"session_{session_id}.json"
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)
        
        if request.lesson_id:
            try:
                lesson_file = DATA_DIR / f"lesson_{request.lesson_id}.json"
                if lesson_file.exists():
                    with open(lesson_file, "r") as f:
                        lesson = json.load(f)
                    rendered_html = generate_rendered_html(lesson, "")
                    rendered_output_dir = DATA_DIR / "rendered"
                    rendered_output_dir.mkdir(exist_ok=True)
                    session_rendered_file = rendered_output_dir / f"session_{session_id}.html"
                    with open(session_rendered_file, "w", encoding="utf-8") as f:
                        f.write(rendered_html)
                    print(f"✅ Generated session rendered output: {session_rendered_file}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to generate session rendered output: {e}")
        
        return {"status": "ok", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save session: {str(e)}")


@app.put("/sessions/{session_id}")
async def update_session(session_id: str, request: SaveSessionRequest):
    """Update an existing session."""
    try:
        session_file = SESSIONS_DIR / f"session_{session_id}.json"
        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")
        
        with open(session_file, "r") as f:
            session_data = json.load(f)
        
        session_data.update({
            "topic": request.topic,
            "lesson_id": request.lesson_id,
            "messages": request.messages,
            "notes": request.notes,
            "session_time": request.session_time,
            "updated_at": datetime.datetime.now().isoformat()
        })
        
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)
        
        if request.lesson_id:
            try:
                lesson_file = DATA_DIR / f"lesson_{request.lesson_id}.json"
                if lesson_file.exists():
                    with open(lesson_file, "r") as f:
                        lesson = json.load(f)
                    rendered_html = generate_rendered_html(lesson, "")
                    rendered_output_dir = DATA_DIR / "rendered"
                    rendered_output_dir.mkdir(exist_ok=True)
                    session_rendered_file = rendered_output_dir / f"session_{session_id}.html"
                    with open(session_rendered_file, "w", encoding="utf-8") as f:
                        f.write(rendered_html)
                    print(f"✅ Updated session rendered output: {session_rendered_file}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to update session rendered output: {e}")
        
        return {"status": "ok", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a session by ID."""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    with open(session_file, "r") as f:
        return json.load(f)


@app.get("/sessions")
async def list_sessions():
    """List all sessions."""
    sessions = []
    for session_file in SESSIONS_DIR.glob("session_*.json"):
        with open(session_file, "r") as f:
            sessions.append(json.load(f))
    
    sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return {"sessions": sessions}


def generate_rendered_html(lesson: Dict[str, Any], api_base: str = "") -> str:
    """Generate fully rendered HTML with animations for a lesson."""
    from pathlib import Path
    
    ASSETS_DIR = Path(__file__).parent / "assets"
    for step in lesson.get('timeline', []):
        for asset in step.get('assets', []):
            if not asset.get('svg') and asset.get('url'):
                asset_file = asset['url'].replace('/assets/', '')
                asset_path = ASSETS_DIR / asset_file
                if asset_path.exists():
                    with open(asset_path, 'r') as f:
                        asset['svg'] = f.read()
    
    total_steps = len(lesson.get('timeline', []))
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Animated Lesson: {lesson.get('topic', 'Untitled')}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .controls {{
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 12px 24px;
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
        }}
        .btn:active {{
            transform: translateY(0);
        }}
        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .step-container {{
            margin: 40px auto;
            max-width: 1200px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            display: none;
        }}
        .step-container.active {{
            display: block;
            animation: fadeIn 0.5s ease-in;
        }}
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        .step-title {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #fff;
            text-align: center;
        }}
        .step-description {{
            font-size: 1.1rem;
            line-height: 1.6;
            color: #d1d5db;
            margin-bottom: 25px;
            text-align: center;
        }}
        .key-points {{
            margin: 25px 0;
            padding: 20px;
            background: rgba(59, 130, 246, 0.1);
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
        }}
        .key-points h3 {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #93c5fd;
        }}
        .key-points ul {{
            list-style: none;
            padding: 0;
        }}
        .key-points li {{
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
            color: #e5e7eb;
            font-size: 1rem;
            opacity: 0;
            transform: translateX(-20px);
        }}
        .key-points li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: bold;
        }}
        .formula-box {{
            margin: 25px 0;
            padding: 20px;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.2));
            border: 2px solid #8b5cf6;
            border-radius: 12px;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 1.5rem;
            font-weight: bold;
            color: #c4b5fd;
            opacity: 0;
            transform: scale(0.9);
        }}
        .asset-container {{
            margin: 30px 0;
            padding: 30px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 300px;
            overflow: hidden;
        }}
        .asset-container svg {{
            max-width: 100%;
            height: auto;
            display: block !important;
            visibility: visible !important;
            opacity: 0;
            transform: scale(0.8);
        }}
        .progress-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            z-index: 1000;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            width: 0%;
            transition: width 0.3s ease;
        }}
        .step-indicator {{
            text-align: center;
            margin-top: 20px;
            color: #9ca3af;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{lesson.get('topic', 'Untitled Lesson')}</h1>
        <p style="color: #9ca3af;">Lesson ID: {lesson.get('lesson_id', 'N/A')}</p>
    </div>
    
    <div class="controls">
        <button class="btn" id="play-btn" onclick="playAnimation()">▶ Play</button>
        <button class="btn" id="pause-btn" onclick="pauseAnimation()" disabled>⏸ Pause</button>
        <button class="btn" id="prev-btn" onclick="previousStep()">⏮ Previous</button>
        <button class="btn" id="next-btn" onclick="nextStep()">Next ⏭</button>
        <button class="btn" id="restart-btn" onclick="restartAnimation()">↻ Restart</button>
    </div>
    
    <div id="lesson-timeline">
"""
    
    for step_idx, step in enumerate(lesson.get('timeline', [])):
        html += f"""
        <div class="step-container" id="step-{step_idx}" {'class="active"' if step_idx == 0 else ''}>
            <div class="step-title">{step.get('title', f'Step {step_idx + 1}')}</div>
            <div class="step-description">{step.get('description', '')}</div>
"""
        if step.get('key_points'):
            html += """
            <div class="key-points">
                <h3>Key Points:</h3>
                <ul>
"""
            for point in step['key_points']:
                html += f'                    <li>{point}</li>\n'
            html += """
                </ul>
            </div>
"""
        
        if step.get('formula'):
            html += f"""
            <div class="formula-box" id="formula-{step_idx}">
                {step['formula']}
            </div>
"""
        
        for asset_idx, asset in enumerate(step.get('assets', [])):
            html += f"""
            <div class="asset-container" id="asset-{step_idx}-{asset_idx}">
"""
            if asset.get('svg'):
                html += asset['svg']
            elif asset.get('url'):
                html += f'<p style="color: #999;">Loading asset from {asset["url"]}...</p>'
            else:
                html += '<p style="color: #999;">No asset available</p>'
            html += """
            </div>
"""
        
        html += f"""
            <div class="step-indicator">Step {step_idx + 1} of {total_steps} • Duration: {step.get('duration_seconds', 15)}s</div>
        </div>
"""
    
    html += """
    </div>
    
    <div class="progress-bar">
        <div class="progress-fill" id="progress-fill"></div>
    </div>
    
    <script>
        let currentStep = 0;
        let isPlaying = false;
        let animationTimers = [];
        const totalSteps = """ + str(total_steps) + """;
        
        function showStep(stepIndex) {
            // Hide all steps
            document.querySelectorAll('.step-container').forEach((step, idx) => {
                step.classList.remove('active');
                if (idx === stepIndex) {
                    step.classList.add('active');
                }
            });
            
            // Update progress
            const progress = ((stepIndex + 1) / totalSteps) * 100;
            document.getElementById('progress-fill').style.width = progress + '%';
            
            // Animate current step
            animateStep(stepIndex);
        }
        
        function animateStep(stepIndex) {
            const stepContainer = document.getElementById('step-' + stepIndex);
            if (!stepContainer) return;
            
            // Clear previous timers
            animationTimers.forEach(timer => clearTimeout(timer));
            animationTimers = [];
            
            console.log('Animating step', stepIndex);
            
            // Animate key points
            const keyPoints = stepContainer.querySelectorAll('.key-points li');
            keyPoints.forEach((point, idx) => {
                const timer = setTimeout(() => {
                    anime({
                        targets: point,
                        opacity: [0, 1],
                        transform: ['translateX(-20px)', 'translateX(0)'],
                        duration: 600,
                        easing: 'easeOutQuad'
                    });
                }, 500 + (idx * 200));
                animationTimers.push(timer);
            });
            
            // Animate formula
            const formula = stepContainer.querySelector('.formula-box');
            if (formula) {
                const timer = setTimeout(() => {
                    anime({
                        targets: formula,
                        opacity: [0, 1],
                        scale: [0.9, 1],
                        duration: 800,
                        easing: 'easeOutQuad'
                    });
                }, 1000);
                animationTimers.push(timer);
            }
            
            // Animate SVGs
            const svgs = stepContainer.querySelectorAll('.asset-container svg');
            svgs.forEach((svg, svgIdx) => {
                const timer = setTimeout(() => {
                    // Fade in and zoom SVG
                    anime({
                        targets: svg,
                        opacity: [0, 1],
                        scale: [0.8, 1],
                        duration: 2000,
                        easing: 'easeOutQuad'
                    });
                    
                    // Animate paths
                    const paths = svg.querySelectorAll('path');
                    paths.forEach((path, pIdx) => {
                        const length = path.getTotalLength();
                        if (length > 0) {
                            path.style.strokeDasharray = length;
                            path.style.strokeDashoffset = length;
                            anime({
                                targets: path,
                                strokeDashoffset: [length, 0],
                                duration: 2500,
                                delay: 500 + (pIdx * 150),
                                easing: 'easeInOutQuad'
                            });
                        }
                    });
                    
                    // Animate lines
                    const lines = svg.querySelectorAll('line');
                    lines.forEach((line, lIdx) => {
                        line.style.opacity = '0';
                        anime({
                            targets: line,
                            opacity: [0, 1],
                            duration: 1000,
                            delay: 800 + (lIdx * 150),
                            easing: 'easeOutQuad'
                        });
                    });
                    
                    // Animate rectangles (text boxes)
                    const rects = svg.querySelectorAll('rect');
                    rects.forEach((rect, rIdx) => {
                        rect.style.opacity = '0';
                        anime({
                            targets: rect,
                            opacity: [0, 1],
                            duration: 1000,
                            delay: 1000 + (rIdx * 150),
                            easing: 'easeOutQuad'
                        });
                    });
                    
                    // Animate text elements
                    const texts = svg.querySelectorAll('text');
                    texts.forEach((text, tIdx) => {
                        text.style.opacity = '0';
                        anime({
                            targets: text,
                            opacity: [0, 1],
                            duration: 800,
                            delay: 1200 + (tIdx * 100),
                            easing: 'easeOutQuad'
                        });
                    });
                    
                    // Animate circles
                    const circles = svg.querySelectorAll('circle');
                    circles.forEach((circle, cIdx) => {
                        circle.style.opacity = '0';
                        anime({
                            targets: circle,
                            opacity: [0, 1],
                            scale: [0.8, 1],
                            duration: 800,
                            delay: 1000 + (cIdx * 100),
                            easing: 'easeOutQuad'
                        });
                    });
                }, svgIdx * 300);
                animationTimers.push(timer);
            });
        }
        
        function playAnimation() {
            if (isPlaying) return;
            isPlaying = true;
            document.getElementById('play-btn').disabled = true;
            document.getElementById('pause-btn').disabled = false;
            
            const step = document.getElementById('step-' + currentStep);
            if (step) {
                const duration = parseInt(step.querySelector('.step-indicator').textContent.match(/Duration: (\\d+)s/)[1]) * 1000;
                
                const timer = setTimeout(() => {
                    if (currentStep < totalSteps - 1) {
                        nextStep();
                    } else {
                        pauseAnimation();
                    }
                }, duration);
                animationTimers.push(timer);
            }
        }
        
        function pauseAnimation() {
            isPlaying = false;
            document.getElementById('play-btn').disabled = false;
            document.getElementById('pause-btn').disabled = true;
            animationTimers.forEach(timer => clearTimeout(timer));
            animationTimers = [];
        }
        
        function nextStep() {
            if (currentStep < totalSteps - 1) {
                currentStep++;
                showStep(currentStep);
                if (isPlaying) {
                    playAnimation();
                }
            }
        }
        
        function previousStep() {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
                if (isPlaying) {
                    playAnimation();
                }
            }
        }
        
        function restartAnimation() {
            pauseAnimation();
            currentStep = 0;
            showStep(currentStep);
        }
        
        // Initialize
        showStep(0);
        
        // Auto-play on load
        setTimeout(() => {
            playAnimation();
        }, 1000);
    </script>
</body>
</html>
"""
    return html


@app.get("/render/{lesson_id}", response_class=HTMLResponse)
async def render_lesson(lesson_id: str, request: StarletteRequest):
    """HTML preview page for a lesson with full animations."""
    lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
    if not lesson_file.exists():
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    with open(lesson_file, "r") as f:
        lesson = json.load(f)
    
    api_base = str(request.base_url).rstrip('/') if hasattr(request, 'base_url') else ""
    html = generate_rendered_html(lesson, api_base)
    return HTMLResponse(content=html)


@app.get("/render/{lesson_id}/embed", response_class=HTMLResponse)
async def render_lesson_embed(lesson_id: str):
    """Embeddable HTML content for a lesson (with inline styles)."""
    lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
    if not lesson_file.exists():
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    with open(lesson_file, "r") as f:
        lesson = json.load(f)
    
    html = generate_rendered_html(lesson, "")
    
    import re
    style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    script_match = re.search(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    
    embed_content = ""
    if style_match:
        embed_content += f"<style>{style_match.group(1)}</style>"
    if body_match:
        embed_content += body_match.group(1)
    if script_match:
        embed_content += f"<script>{script_match.group(1)}</script>"
    
    if embed_content:
        return HTMLResponse(content=embed_content)
    return HTMLResponse(content=html)


@app.get("/sessions/{session_id}/render", response_class=HTMLResponse)
async def render_session(session_id: str, request: StarletteRequest):
    """Get rendered HTML output for a session."""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    with open(session_file, "r") as f:
        session_data = json.load(f)
    
    lesson_id = session_data.get("lesson_id")
    if not lesson_id:
        raise HTTPException(status_code=404, detail="Session has no associated lesson")
    
    rendered_output_dir = DATA_DIR / "rendered"
    session_rendered_file = rendered_output_dir / f"session_{session_id}.html"
    
    if session_rendered_file.exists():
        with open(session_rendered_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
        if not lesson_file.exists():
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        with open(lesson_file, "r") as f:
            lesson = json.load(f)
        
        api_base = str(request.base_url).rstrip('/')
        html = generate_rendered_html(lesson, api_base)
        
        rendered_output_dir.mkdir(exist_ok=True)
        with open(session_rendered_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        return HTMLResponse(content=html)


@app.get("/sessions/{session_id}/render/embed", response_class=HTMLResponse)
async def render_session_embed(session_id: str):
    """Get embeddable rendered HTML for a session."""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    with open(session_file, "r") as f:
        session_data = json.load(f)
    
    lesson_id = session_data.get("lesson_id")
    if not lesson_id:
        raise HTTPException(status_code=404, detail="Session has no associated lesson")
    
    lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
    if not lesson_file.exists():
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    with open(lesson_file, "r") as f:
        lesson = json.load(f)
    
    html = generate_rendered_html(lesson, "")
    
    import re
    style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    script_match = re.search(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    
    embed_content = ""
    if style_match:
        embed_content += f"<style>{style_match.group(1)}</style>"
    if body_match:
        embed_content += body_match.group(1)
    if script_match:
        embed_content += f"<script>{script_match.group(1)}</script>"
    
    if embed_content:
        return HTMLResponse(content=embed_content)
    return HTMLResponse(content=html)


@app.get("/rendered")
async def list_rendered_outputs():
    """List all rendered output files."""
    rendered_output_dir = DATA_DIR / "rendered"
    rendered_output_dir.mkdir(exist_ok=True)
    
    rendered_files = []
    for file in rendered_output_dir.glob("*.html"):
        stat = file.stat()
        file_type = "lesson" if file.name.startswith("lesson_") else "session"
        file_id = file.stem.replace("lesson_", "").replace("session_", "")
        
        rendered_files.append({
            "filename": file.name,
            "id": file_id,
            "type": file_type,
            "size": stat.st_size,
            "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "url": f"/rendered/{file.name}",
            "render_url": f"/render/{file_id}" if file_type == "lesson" else f"/sessions/{file_id}/render"
        })
    
    rendered_files.sort(key=lambda x: x["modified"], reverse=True)
    
    return {"rendered_files": rendered_files, "count": len(rendered_files)}


@app.get("/rendered/{filename}")
async def get_rendered_output(filename: str):
    """Get a specific rendered output file."""
    rendered_output_dir = DATA_DIR / "rendered"
    rendered_file = rendered_output_dir / filename
    
    if not rendered_file.exists():
        raise HTTPException(status_code=404, detail="Rendered file not found")
    
    if not filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    with open(rendered_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

