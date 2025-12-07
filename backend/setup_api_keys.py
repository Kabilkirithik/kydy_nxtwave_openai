#!/usr/bin/env python3
"""
Interactive script to set up API keys for Kydy backend.
"""
import os
from pathlib import Path

def setup_api_keys():
    """Interactive API key setup."""
    print("=" * 50)
    print("Kydy Backend API Key Setup")
    print("=" * 50)
    print()
    
    env_file = Path(__file__).parent / ".env"
    
    existing_keys = {}
    if env_file.exists():
        print("⚠️  .env file already exists.")
        response = input("Do you want to update it? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping setup.")
            return
        
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    existing_keys[key] = value
    
    print()
    print("1. Google Gemini API Key")
    print("   Get it from: https://makersuite.google.com/app/apikey")
    if existing_keys.get('GEMINI_API_KEY'):
        print(f"   Current: {existing_keys['GEMINI_API_KEY'][:20]}...")
        response = input("   Update? (y/n, or press Enter to skip): ").strip().lower()
        if response == 'y':
            gemini_key = input("   Enter Gemini API Key: ").strip()
        else:
            gemini_key = existing_keys.get('GEMINI_API_KEY', '')
    else:
        gemini_key = input("   Enter Gemini API Key (or press Enter to skip): ").strip()
    
    print()
    print("2. Hugging Face API Token")
    print("   Get it from: https://huggingface.co/settings/tokens")
    if existing_keys.get('HF_API_TOKEN'):
        print(f"   Current: {existing_keys['HF_API_TOKEN'][:20]}...")
        response = input("   Update? (y/n, or press Enter to skip): ").strip().lower()
        if response == 'y':
            hf_token = input("   Enter Hugging Face API Token: ").strip()
        else:
            hf_token = existing_keys.get('HF_API_TOKEN', '')
    else:
        hf_token = input("   Enter Hugging Face API Token (or press Enter to skip): ").strip()
    
    print()
    print("Writing to .env file...")
    
    lines = []
    if gemini_key:
        lines.append(f"GEMINI_API_KEY={gemini_key}\n")
    if hf_token:
        lines.append(f"HF_API_TOKEN={hf_token}\n")
    
    if lines:
        with open(env_file, 'w') as f:
            f.writelines(lines)
        print("✅ API keys saved to .env file")
    else:
        print("⏭️  No API keys provided (system will use fallbacks)")
    
    print()
    print("Setup complete!")
    print()
    print("Next steps:")
    print("1. Install python-dotenv: pip install python-dotenv")
    print("2. Restart the backend server")
    print("3. Check health: curl http://localhost:8000/health")
    print()

if __name__ == "__main__":
    setup_api_keys()

