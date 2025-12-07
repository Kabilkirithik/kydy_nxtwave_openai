"""
Gemini LLM client for extracting lesson structure from prompts.
"""
import os
import json
import re
from typing import Dict, Any, Optional


class GeminiClient:
    """Client for Google Gemini API."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    def extract_lesson_structure(self, prompt: str) -> Dict[str, Any]:
        """
        Extract structured lesson data from user prompt.
        Returns dict with: topic, subtopic, intent, audience, suggested_steps, primitives, learning_objectives
        """
        if not self.api_key:
            print("GEMINI_API_KEY not set, using fallback extraction")
            return self._fallback_extraction(prompt)
        
        try:
            system_prompt = """You are an educational content generator. Extract structured lesson information from the user's prompt.

Return ONLY valid JSON (no markdown, no code blocks) with this exact structure:
{
  "topic": "Main topic name",
  "subtopic": "Specific subtopic",
  "intent": "educational|tutorial|demonstration",
  "audience": "beginner|intermediate|advanced",
  "suggested_steps": [
    {
      "title": "Step title",
      "description": "Detailed step description explaining the concept clearly",
      "key_points": ["Point 1", "Point 2", "Point 3"],
      "formula": "Optional formula if applicable",
      "duration_seconds": 30
    }
  ],
  "primitives": [
    {
      "primitive_id": "resistor|battery|stethoscope|graph",
      "params": {}
    }
  ],
  "learning_objectives": ["Objective 1", "Objective 2"]
}

IMPORTANT:
- Generate 3-5 detailed steps with rich descriptions
- Each step should have key_points array with 2-4 bullet points
- Include formulas if the topic involves calculations
- Make descriptions educational and clear (at least 50 words per step)
- For primitives, choose from: resistor, battery, stethoscope, graph
- Add params if needed (e.g., {"value": "10k"} for resistor, {"voltage": "9V"} for battery)
- Distribute primitives across steps (each step should have at least one)"""
            
            full_prompt = f"{system_prompt}\n\nUser prompt: {prompt}\n\nJSON:"
            
            response = self._call_gemini(full_prompt)
            return self._parse_json_response(response)
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            return self._fallback_extraction(prompt)
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        try:
            import requests
        except ImportError:
            raise ImportError("requests package is required. Install it with: pip install requests")
        
        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")
        
        raise ValueError("No content in Gemini response")
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response text."""
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        
        try:
            return json.loads(text)
        except:
            raise ValueError("Could not parse JSON from response")
    
    def _fallback_extraction(self, prompt: str) -> Dict[str, Any]:
        """Fallback extraction when Gemini is unavailable."""
        prompt_lower = prompt.lower()
        
        primitives = []
        if "resistor" in prompt_lower or "ohm" in prompt_lower or "circuit" in prompt_lower:
            primitives.append({"primitive_id": "resistor", "params": {"value": "10kΩ"}})
            primitives.append({"primitive_id": "battery", "params": {"voltage": "9V"}})
            primitives.append({"primitive_id": "graph", "params": {}})
        elif "battery" in prompt_lower or "voltage" in prompt_lower or "power" in prompt_lower:
            primitives.append({"primitive_id": "battery", "params": {"voltage": "12V"}})
            primitives.append({"primitive_id": "graph", "params": {}})
        elif "stethoscope" in prompt_lower or "medical" in prompt_lower or "heart" in prompt_lower:
            primitives.append({"primitive_id": "stethoscope", "params": {}})
            primitives.append({"primitive_id": "graph", "params": {}})
        else:
            primitives.append({"primitive_id": "graph", "params": {}})
            primitives.append({"primitive_id": "graph", "params": {"points": [10, 30, 20, 40, 35, 50, 45, 60]}})
        
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
        else:
            steps = [
                {
                    "title": "Introduction",
                    "description": f"Welcome to this lesson about {prompt[:50]}. We'll explore the fundamental concepts and build a solid understanding step by step. This topic is important because it forms the foundation for deeper learning.",
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
        
        return {
            "topic": prompt[:60] if len(prompt) > 60 else prompt,
            "subtopic": "Introduction",
            "intent": "educational",
            "audience": "beginner",
            "suggested_steps": steps,
            "primitives": primitives,
            "learning_objectives": ["Understand the core concepts", "Apply knowledge practically", "Build a solid foundation"]
        }

