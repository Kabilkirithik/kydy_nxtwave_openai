"""
Script to enhance an existing lesson with key_points and formulas for testing.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def enhance_lesson(lesson_id):
    """Add key_points and formulas to an existing lesson."""
    lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
    
    if not lesson_file.exists():
        print(f"Lesson file not found: {lesson_file}")
        return
    
    with open(lesson_file, "r") as f:
        lesson = json.load(f)
    
    for step in lesson.get('timeline', []):
        if step.get('title', '').lower().startswith('introduction'):
            step['key_points'] = [
                "Ohm's Law: V = I × R",
                "Voltage (V) is measured in volts",
                "Current (I) is measured in amperes",
                "Resistance (R) is measured in ohms"
            ]
            step['formula'] = "V = I × R"
            step['description'] = "Ohm's Law is a fundamental principle in electrical engineering that describes the relationship between voltage, current, and resistance in an electrical circuit. It states that the current through a conductor between two points is directly proportional to the voltage across the two points and inversely proportional to the resistance between them."
        elif 'concept' in step.get('title', '').lower() or 'main' in step.get('title', '').lower():
            step['key_points'] = [
                "Resistance opposes current flow",
                "Measured in ohms (Ω)",
                "Color bands indicate resistance value",
                "Higher resistance = less current flow"
            ]
            step['description'] = "Resistance is the opposition to the flow of electric current. In a resistor, resistance is determined by the material, length, and cross-sectional area. Color-coded bands on resistors indicate their resistance value, making it easy to identify components in circuits."
        else:
            step['key_points'] = [
                "Calculate voltage: V = I × R",
                "Calculate current: I = V / R",
                "Calculate resistance: R = V / I",
                "All three are interconnected"
            ]
            step['formula'] = "I = V / R"
            step['description'] = "When analyzing circuits with Ohm's Law, we can calculate any one of the three variables (voltage, current, or resistance) if we know the other two. This makes circuit design and troubleshooting much easier."
    
    with open(lesson_file, "w") as f:
        json.dump(lesson, f, indent=2)
    
    print(f"✅ Enhanced lesson {lesson_id}")
    print(f"   Added key_points and formulas to {len(lesson.get('timeline', []))} steps")

if __name__ == "__main__":
    import sys
    lesson_id = sys.argv[1] if len(sys.argv) > 1 else "1f6f838b"
    enhance_lesson(lesson_id)

