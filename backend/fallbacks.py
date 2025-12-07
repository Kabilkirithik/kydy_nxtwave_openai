"""
Parametric SVG generators for fallback primitives.
"""
from typing import Dict, Any


class ParametricSVGGenerator:
    """Generate parametric SVG primitives."""
    
    def generate(self, primitive_id: str, params: Dict[str, Any] = None) -> str:
        """Generate SVG for a primitive type."""
        params = params or {}
        
        if primitive_id == "resistor":
            return self._generate_resistor(params)
        elif primitive_id == "battery":
            return self._generate_battery(params)
        elif primitive_id == "stethoscope":
            return self._generate_stethoscope(params)
        elif primitive_id == "graph":
            return self._generate_graph(params)
        else:
            return self._generate_graph(params)  # Default fallback
    
    def _generate_resistor(self, params: Dict[str, Any]) -> str:
        """Generate resistor SVG with text box."""
        value = params.get("value", "10kΩ")
        width = 400
        height = 200
        
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="resistorGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#8B4513;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#A0522D;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8B4513;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#f5f5f5" rx="8"/>
  
  <!-- Text box -->
  <rect x="20" y="20" width="360" height="60" fill="#fff" stroke="#3b82f6" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="{width/2}" y="45" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1e40af" text-anchor="middle" opacity="0">Resistor Component</text>
  <text x="{width/2}" y="65" font-family="Arial, sans-serif" font-size="14" fill="#4b5563" text-anchor="middle" opacity="0">Resistance: {value}</text>
  
  <!-- Circuit diagram -->
  <g transform="translate(50, 120)">
    <!-- Left wire -->
    <line x1="0" y1="0" x2="60" y2="0" stroke="#333" stroke-width="4" stroke-linecap="round"/>
    <!-- Resistor body -->
    <rect x="60" y="-25" width="140" height="50" fill="url(#resistorGrad)" stroke="#654321" stroke-width="3" rx="6" opacity="0"/>
    <!-- Color bands -->
    <rect x="75" y="-25" width="10" height="50" fill="#000" opacity="0"/>
    <rect x="95" y="-25" width="10" height="50" fill="#8B0000" opacity="0"/>
    <rect x="115" y="-25" width="10" height="50" fill="#FFD700" opacity="0"/>
    <rect x="135" y="-25" width="10" height="50" fill="#C0C0C0" opacity="0"/>
    <!-- Right wire -->
    <line x1="200" y1="0" x2="260" y2="0" stroke="#333" stroke-width="4" stroke-linecap="round"/>
    <!-- Value label below -->
    <text x="130" y="40" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e40af" text-anchor="middle" opacity="0">{value}</text>
  </g>
  
  <!-- Formula box (if applicable) -->
  <rect x="20" y="140" width="360" height="40" fill="#e0e7ff" stroke="#6366f1" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="{width/2}" y="165" font-family="Arial, sans-serif" font-size="14" fill="#4338ca" text-anchor="middle" opacity="0">R = Resistance (Ω)</text>
</svg>'''
    
    def _generate_battery(self, params: Dict[str, Any]) -> str:
        """Generate battery SVG with text box."""
        voltage = params.get("voltage", "9V")
        width = 400
        height = 250
        
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="batteryGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#2E7D32;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1B5E20;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#f5f5f5" rx="8"/>
  
  <!-- Text box -->
  <rect x="20" y="20" width="360" height="70" fill="#fff" stroke="#10b981" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="{width/2}" y="45" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#065f46" text-anchor="middle" opacity="0">Battery Component</text>
  <text x="{width/2}" y="70" font-family="Arial, sans-serif" font-size="14" fill="#4b5563" text-anchor="middle" opacity="0">Voltage: {voltage}</text>
  
  <!-- Battery diagram -->
  <g transform="translate({width/2 - 60}, 120)">
    <!-- Battery body -->
    <rect x="0" y="0" width="80" height="100" fill="url(#batteryGrad)" stroke="#1B5E20" stroke-width="3" rx="5" opacity="0"/>
    <!-- Positive terminal -->
    <rect x="25" y="-15" width="30" height="15" fill="#1B5E20" stroke="#0D4A0F" stroke-width="2" rx="3" opacity="0"/>
    <!-- Negative terminal -->
    <rect x="30" y="100" width="20" height="15" fill="#1B5E20" stroke="#0D4A0F" stroke-width="2" rx="3" opacity="0"/>
    <!-- Voltage label -->
    <text x="40" y="130" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#065f46" text-anchor="middle" opacity="0">{voltage}</text>
    <!-- Plus sign -->
    <text x="40" y="10" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#fff" text-anchor="middle" opacity="0">+</text>
    <!-- Minus sign -->
    <text x="40" y="110" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#fff" text-anchor="middle" opacity="0">-</text>
  </g>
  
  <!-- Info box -->
  <rect x="20" y="200" width="360" height="35" fill="#d1fae5" stroke="#10b981" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="{width/2}" y="222" font-family="Arial, sans-serif" font-size="13" fill="#065f46" text-anchor="middle" opacity="0">Provides electrical energy to the circuit</text>
</svg>'''
    
    def _generate_stethoscope(self, params: Dict[str, Any]) -> str:
        """Generate stethoscope SVG with text box."""
        width = 450
        height = 500
        
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="tubeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#4169E1;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1E90FF;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#f5f5f5" rx="8"/>
  
  <!-- Title box -->
  <rect x="20" y="20" width="410" height="60" fill="#fff" stroke="#6366f1" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="{width/2}" y="45" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#4338ca" text-anchor="middle" opacity="0">Stethoscope</text>
  <text x="{width/2}" y="65" font-family="Arial, sans-serif" font-size="14" fill="#6b7280" text-anchor="middle" opacity="0">Medical diagnostic instrument</text>
  
  <!-- Stethoscope diagram -->
  <g transform="translate({width/2 - 75}, 100)">
    <!-- Chest piece -->
    <circle cx="75" cy="0" r="35" fill="#C0C0C0" stroke="#808080" stroke-width="3" opacity="0"/>
    <circle cx="75" cy="0" r="25" fill="#E0E0E0" stroke="#A0A0A0" stroke-width="2" opacity="0"/>
    <!-- Y-connector -->
    <path d="M 75 35 L 45 100 L 105 100 Z" fill="#4169E1" stroke="#1E3A8A" stroke-width="2" opacity="0"/>
    <!-- Left tube -->
    <path d="M 45 100 Q 15 170 -5 240" 
          stroke="url(#tubeGrad)" stroke-width="8" fill="none" stroke-linecap="round" opacity="0"/>
    <!-- Right tube -->
    <path d="M 105 100 Q 135 170 155 240" 
          stroke="url(#tubeGrad)" stroke-width="8" fill="none" stroke-linecap="round" opacity="0"/>
    <!-- Left earpiece -->
    <circle cx="-5" cy="240" r="15" fill="#4169E1" stroke="#1E3A8A" stroke-width="2" opacity="0"/>
    <circle cx="-5" cy="240" r="8" fill="#1E90FF" opacity="0"/>
    <!-- Right earpiece -->
    <circle cx="155" cy="240" r="15" fill="#4169E1" stroke="#1E3A8A" stroke-width="2" opacity="0"/>
    <circle cx="155" cy="240" r="8" fill="#1E90FF" opacity="0"/>
  </g>
  
  <!-- Info boxes -->
  <rect x="20" y="360" width="200" height="60" fill="#e0e7ff" stroke="#6366f1" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="120" y="385" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#4338ca" text-anchor="middle" opacity="0">Chest Piece</text>
  <text x="120" y="405" font-family="Arial, sans-serif" font-size="12" fill="#4b5563" text-anchor="middle" opacity="0">Detects sounds</text>
  
  <rect x="230" y="360" width="200" height="60" fill="#e0e7ff" stroke="#6366f1" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="330" y="385" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#4338ca" text-anchor="middle" opacity="0">Earpieces</text>
  <text x="330" y="405" font-family="Arial, sans-serif" font-size="12" fill="#4b5563" text-anchor="middle" opacity="0">Amplify sounds</text>
  
  <!-- Usage box -->
  <rect x="20" y="430" width="410" height="55" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="{width/2}" y="455" font-family="Arial, sans-serif" font-size="13" fill="#1e40af" text-anchor="middle" opacity="0">Used to listen to internal body sounds</text>
  <text x="{width/2}" y="475" font-family="Arial, sans-serif" font-size="12" fill="#4b5563" text-anchor="middle" opacity="0">Heart, lungs, and blood flow</text>
</svg>'''
    
    def _generate_graph(self, params: Dict[str, Any]) -> str:
        """Generate graph/chart SVG with text box."""
        width = 500
        height = 400
        data_points = params.get("points", [10, 30, 20, 40, 35, 50, 45])
        graph_title = params.get("title", "Data Visualization")
        
        max_val = max(data_points) if data_points else 50
        normalized = [int((p / max_val) * 200) for p in data_points]
        
        path_d = f"M 80 {height - 80 - normalized[0]}"
        for i, val in enumerate(normalized[1:], 1):
            x = 80 + (i * 60)
            y = height - 80 - val
            path_d += f" L {x} {y}"
        
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
      <path d="M 60 0 L 0 0 0 60" fill="none" stroke="#e0e0e0" stroke-width="1"/>
    </pattern>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#f5f5f5" rx="8"/>
  
  <!-- Title box -->
  <rect x="20" y="20" width="460" height="50" fill="#fff" stroke="#3b82f6" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="{width/2}" y="45" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#1e40af" text-anchor="middle" opacity="0">{graph_title}</text>
  <text x="{width/2}" y="65" font-family="Arial, sans-serif" font-size="12" fill="#6b7280" text-anchor="middle" opacity="0">Visual representation of data over time</text>
  
  <!-- Graph area -->
  <g transform="translate(0, 90)">
    <rect x="60" y="0" width="420" height="250" fill="url(#grid)" opacity="0"/>
    <!-- Axes -->
    <line x1="80" y1="250" x2="460" y2="250" stroke="#333" stroke-width="3" opacity="0"/>
    <line x1="80" y1="20" x2="80" y2="250" stroke="#333" stroke-width="3" opacity="0"/>
    <!-- Data line -->
    <path d="{path_d}" fill="none" stroke="#3b82f6" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0"/>
    <!-- Data points -->
    {''.join([f'<circle cx="{80 + i * 60}" cy="{250 - normalized[i]}" r="6" fill="#3b82f6" opacity="0"/>' for i in range(len(normalized))])}
    <!-- Labels -->
    <text x="{width/2}" y="290" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#374151" text-anchor="middle" opacity="0">Time</text>
    <text x="30" y="145" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#374151" text-anchor="middle" transform="rotate(-90 30 145)" opacity="0">Value</text>
  </g>
  
  <!-- Stats box -->
  <rect x="20" y="340" width="460" height="45" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6" filter="url(#shadow)" opacity="0"/>
  <text x="250" y="360" font-family="Arial, sans-serif" font-size="12" fill="#1e40af" text-anchor="middle" opacity="0">Max: {max(data_points) if data_points else 0} | Min: {min(data_points) if data_points else 0} | Avg: {int(sum(data_points)/len(data_points)) if data_points else 0}</text>
</svg>'''

