"""
Pytest tests for backend endpoints.
"""
try:
    import pytest
    from fastapi.testclient import TestClient
except ImportError as e:
    pytest = None  # type: ignore
    TestClient = None  # type: ignore
    print(f"Warning: Test dependencies not installed: {e}")
    print("Install with: pip install pytest fastapi")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app import app
except ImportError:
    app = None  # type: ignore
    print("Warning: Could not import app")

if pytest is not None and TestClient is not None and app is not None:
    client = TestClient(app)
else:
    client = None  # type: ignore


def test_generate_endpoint():
    """Test /generate endpoint returns 200 and expected fields."""
    if client is None:
        pytest.skip("TestClient not available")
    response = client.post(
        "/generate",
        json={"prompt": "Teach me Ohm's Law with a resistor and battery"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert "lesson_id" in data
    assert "render_url" in data
    assert "lesson" in data
    
    lesson = data["lesson"]
    assert "topic" in lesson
    assert "timeline" in lesson
    assert isinstance(lesson["timeline"], list)
    
    if lesson["timeline"]:
        step = lesson["timeline"][0]
        assert "title" in step
        assert "assets" in step


def test_get_lesson_endpoint():
    """Test /lesson/{id} endpoint."""
    if client is None:
        pytest.skip("TestClient not available")
    generate_response = client.post(
        "/generate",
        json={"prompt": "Test lesson"}
    )
    assert generate_response.status_code == 200
    lesson_id = generate_response.json()["lesson_id"]
    
    response = client.get(f"/lesson/{lesson_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["lesson_id"] == lesson_id
    assert "timeline" in data


def test_get_lesson_not_found():
    """Test /lesson/{id} returns 404 for non-existent lesson."""
    if client is None:
        pytest.skip("TestClient not available")
    response = client.get("/lesson/nonexistent")
    assert response.status_code == 404


def test_render_endpoint():
    """Test /render/{id} returns HTML."""
    if client is None:
        pytest.skip("TestClient not available")
    generate_response = client.post(
        "/generate",
        json={"prompt": "Test lesson for rendering"}
    )
    assert generate_response.status_code == 200
    lesson_id = generate_response.json()["lesson_id"]
    
    response = client.get(f"/render/{lesson_id}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert lesson_id in response.text

