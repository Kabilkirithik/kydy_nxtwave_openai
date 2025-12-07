# API Keys Setup Guide

This guide will help you set up the required API keys for the Kydy lesson generator.

## Required API Keys

The system works with **fallbacks** even without API keys, but for best results, you'll want:

1. **GEMINI_API_KEY** - For extracting lesson structure from prompts (Google Gemini)
2. **HF_API_TOKEN** - For generating SVG illustrations (Hugging Face StarVector)

## Option 1: Interactive Setup Script (Recommended)

Run the setup script:

```bash
cd backend
./setup_env.sh
```

This will prompt you for your API keys and create a `.env` file.

## Option 2: Manual Setup

### Step 1: Create .env file

In the `backend/` directory, create a `.env` file:

```bash
cd backend
cp .env.example .env
```

### Step 2: Add your API keys

Edit the `.env` file and add your keys:

```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
HF_API_TOKEN=your-actual-huggingface-token-here
```

## Getting API Keys

### Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Paste it into your `.env` file as `GEMINI_API_KEY`

**Note**: Gemini API has a free tier with generous limits.

### Hugging Face API Token

1. Go to [Hugging Face](https://huggingface.co/)
2. Sign up or log in
3. Go to your [Settings > Access Tokens](https://huggingface.co/settings/tokens)
4. Click "New token"
5. Give it a name (e.g., "kydy-starvector")
6. Select "Read" permission
7. Copy the token
8. Paste it into your `.env` file as `HF_API_TOKEN`

**Note**: Hugging Face tokens are free for inference API usage.

## Loading Environment Variables

### Automatic (with python-dotenv)

The backend automatically loads `.env` files if `python-dotenv` is installed:

```bash
pip install python-dotenv
```

### Manual (export)

If you prefer to export manually:

```bash
export GEMINI_API_KEY="your-key"
export HF_API_TOKEN="your-token"
```

Or load from .env:

```bash
export $(cat backend/.env | xargs)
```

## Verifying Setup

### Check Backend Health

After starting the backend, check the health endpoint:

```bash
curl http://localhost:8000/health
```

Response should show:
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "hf_configured": true
}
```

### Test Generation

Try generating a lesson:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Teach me Ohm'\''s Law"}'
```

If API keys are working, you'll get better structured lessons. If not, the system will use fallbacks.

## Fallback Behavior

The system is designed to work **without API keys**:

- **Without GEMINI_API_KEY**: Uses keyword-based extraction (still works, but less structured)
- **Without HF_API_TOKEN**: Uses parametric SVG generators (resistor, battery, stethoscope, graph)

You can test the system immediately without any API keys!

## Security Notes

⚠️ **Important**:
- Never commit `.env` files to git (they're in `.gitignore`)
- Don't share your API keys publicly
- Rotate keys if they're exposed
- Use environment variables in production, not `.env` files

## Troubleshooting

### Keys not loading?

1. Check `.env` file is in `backend/` directory
2. Verify `python-dotenv` is installed: `pip install python-dotenv`
3. Restart the backend server after adding keys
4. Check for typos in variable names (must be exactly `GEMINI_API_KEY` and `HF_API_TOKEN`)

### Getting API errors?

1. Verify keys are valid (test them separately)
2. Check API quotas/limits
3. Check network connectivity
4. Review backend logs for specific error messages

### Still having issues?

The system works with fallbacks - you can use it without API keys for testing!

