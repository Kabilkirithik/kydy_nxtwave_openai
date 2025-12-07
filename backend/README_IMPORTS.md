# Import Errors - Resolution Guide

## Overview
If you see import errors in your IDE for `requests`, `lxml`, `pytest`, or `fastapi`, this is normal if the packages aren't installed in your current Python environment.

## Solution

### Option 1: Install Packages Globally (Quick)
```bash
cd backend
pip3 install -r requirements.txt
```

### Option 2: Use Virtual Environment (Recommended)
```bash
cd backend
./setup_venv.sh
source .venv/bin/activate
```

### Option 3: Suppress IDE Warnings
The code is already configured to handle missing imports gracefully:
- All imports are wrapped in try/except blocks
- The code will work even if some packages are missing (with reduced functionality)
- IDE warnings can be safely ignored if packages are installed at runtime

## IDE Configuration

The project includes configuration files to suppress import warnings:
- `backend/pyrightconfig.json` - Pyright/Pylance configuration
- `.vscode/settings.json` - VS Code Python settings

These files configure the IDE to:
- Not report missing imports as errors
- Use basic type checking mode
- Handle graceful degradation

## Package Status

All required packages are listed in `backend/requirements.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `requests` - HTTP client
- `lxml` - XML/SVG processing
- `pydantic` - Data validation
- `pytest` - Testing framework
- `python-dotenv` - Environment variables

## Runtime Behavior

The code handles missing packages gracefully:
- **requests**: Used in `gemini_client.py` and `starvector_client.py` - will raise ImportError with helpful message
- **lxml**: Used in `starvector_client.py` - falls back to regex-based sanitization
- **pytest/fastapi**: Used in tests - tests will be skipped if not available

## Verification

To verify packages are installed:
```bash
python3 -c "import requests, lxml, pytest, fastapi; print('All packages installed!')"
```

If you see no errors, all packages are installed correctly.

