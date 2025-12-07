"""
Test script to render a lesson with full animations and save HTML output for testing.
"""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

def test_render_lesson(lesson_id):
    """Render a lesson to HTML file with full animations for testing."""
    lesson_file = DATA_DIR / f"lesson_{lesson_id}.json"
    
    if not lesson_file.exists():
        print(f"Lesson file not found: {lesson_file}")
        return
    
    with open(lesson_file, "r") as f:
        lesson = json.load(f)
    
    print(f"Lesson ID: {lesson['lesson_id']}")
    print(f"Topic: {lesson['topic']}")
    print(f"Timeline steps: {len(lesson['timeline'])}")
    
    for idx, step in enumerate(lesson['timeline']):
        print(f"\nStep {idx}: {step['title']}")
        print(f"  Duration: {step['duration_seconds']}s")
        print(f"  Key Points: {len(step.get('key_points', []))}")
        print(f"  Formula: {step.get('formula', 'None')}")
        print(f"  Assets: {len(step.get('assets', []))}")
        for asset_idx, asset in enumerate(step.get('assets', [])):
            print(f"    Asset {asset_idx}: {asset.get('primitive_id', 'unknown')}")
            print(f"      URL: {asset.get('url', 'N/A')}")
            print(f"      Has inline SVG: {bool(asset.get('svg'))}")
            if asset.get('svg'):
                svg_len = len(asset['svg'])
                print(f"      SVG length: {svg_len} chars")
    
    for step in lesson['timeline']:
        for asset in step.get('assets', []):
            if not asset.get('svg') and asset.get('url'):
                asset_file = asset['url'].replace('/assets/', '')
                asset_path = ASSETS_DIR / asset_file
                if asset_path.exists():
                    with open(asset_path, 'r') as f:
                        asset['svg'] = f.read()
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Animated Lesson: {lesson['topic']}</title>
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
        <h1>{lesson['topic']}</h1>
        <p style="color: #9ca3af;">Lesson ID: {lesson['lesson_id']}</p>
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
    
    for step_idx, step in enumerate(lesson['timeline']):
        html += f"""
        <div class="step-container" id="step-{step_idx}" {'class="active"' if step_idx == 0 else ''}>
            <div class="step-title">{step['title']}</div>
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
            <div class="step-indicator">Step {step_idx + 1} of {len(lesson['timeline'])} • Duration: {step.get('duration_seconds', 15)}s</div>
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
        const totalSteps = """ + str(len(lesson['timeline'])) + """;
        
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
    
    output_file = DATA_DIR / f"test_render_{lesson_id}.html"
    with open(output_file, "w") as f:
        f.write(html)
    
    print(f"\n✅ Test HTML saved to: {output_file}")
    print(f"Open it in a browser to test rendering")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lesson_id = sys.argv[1]
    else:
        lesson_files = sorted(DATA_DIR.glob("lesson_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if lesson_files:
            lesson_id = lesson_files[0].stem.replace("lesson_", "")
        else:
            print("No lesson files found")
            sys.exit(1)
    
    test_render_lesson(lesson_id)

