"""
Hugging Face StarVector client for SVG generation.
"""
import os
import re
from typing import Optional

try:
    from lxml import etree
except ImportError:
    etree = None  # type: ignore
    print("Warning: lxml not installed. SVG validation will be limited. Install with: pip install lxml")


class StarVectorClient:
    """Client for Hugging Face StarVector Inference API."""
    
    def __init__(self):
        self.api_token = os.getenv("HF_API_TOKEN")

        self.api_url = "https://api-inference.huggingface.co/models/starvector/starvector-1b-im2svg"
    
    def generate_svg(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """
        Generate SVG from text prompt using StarVector.
        Returns SVG string or None on failure.
        """
        if not self.api_token:
            print("HF_API_TOKEN not set, skipping StarVector generation")
            return None
        
        for attempt in range(max_retries + 1):
            try:
                try:
                    import requests
                except ImportError:
                    raise ImportError("requests package is required. Install it with: pip install requests")

                headers = {"Authorization": f"Bearer {self.api_token}"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 2048
                    }
                }

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()

                svg = self._extract_svg_from_response(response.text)
                return svg

            except Exception as e:
                if attempt < max_retries:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                print(f"StarVector generation failed after {max_retries + 1} attempts: {e}")
                return None
        
        return None
    
    def _extract_svg_from_response(self, response_text: str) -> Optional[str]:
        """Extract SVG block from API response."""
        svg_match = re.search(
            r'<svg[^>]*>.*?</svg>',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        if svg_match:
            return svg_match.group(0)
        return None
    
    def is_valid_svg(self, svg_content: str) -> bool:
        """Validate SVG content using lxml."""
        if not svg_content or not svg_content.strip():
            return False
        
        if etree is None:
            return bool(re.search(r'<svg[^>]*>', svg_content, re.IGNORECASE))
        
        try:
            sanitized = self.sanitize_svg(svg_content)
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(sanitized.encode(), parser=parser)
            
            return root.tag.endswith("svg") or root.tag == "svg"
        except Exception as e:
            print(f"SVG validation failed: {e}")
            return False
    
    def sanitize_svg(self, svg_content: str) -> str:
        """Remove dangerous elements from SVG."""
        svg_content = re.sub(r'<script[^>]*>.*?</script>', '', svg_content, flags=re.DOTALL | re.IGNORECASE)
        svg_content = re.sub(r'<foreignObject[^>]*>.*?</foreignObject>', '', svg_content, flags=re.DOTALL | re.IGNORECASE)
        svg_content = re.sub(r'<image[^>]*>', '', svg_content, flags=re.IGNORECASE)
        svg_content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', svg_content, flags=re.IGNORECASE)
        return svg_content
    
    def extract_dimensions(self, svg_content: str) -> tuple[int, int]:
        """Extract width and height from SVG."""
        width_match = re.search(r'width\s*=\s*["\']?(\d+)', svg_content, re.IGNORECASE)
        height_match = re.search(r'height\s*=\s*["\']?(\d+)', svg_content, re.IGNORECASE)
        
        width = int(width_match.group(1)) if width_match else 400
        height = int(height_match.group(1)) if height_match else 300
        
        return width, height
