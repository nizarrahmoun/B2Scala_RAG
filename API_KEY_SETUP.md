# API Key Setup Guide

## Getting Your NVIDIA API Key

1. **Visit NVIDIA Build Platform**
   - Go to [https://build.nvidia.com/](https://build.nvidia.com/)
   - Sign up or log in to your NVIDIA account

2. **Create an API Key**
   - Navigate to the API Keys section
   - Click "Generate API Key"
   - Copy your new API key (starts with `nvapi-`)

## Setting Up the API Key

### Option 1: Using .env File (Recommended)

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file:**
   ```bash
   # Open .env in your text editor and add:
   NVIDIA_API_KEY=nvapi-YOUR_ACTUAL_API_KEY_HERE
   ```

### Option 2: Using Environment Variables

**Windows (PowerShell):**
```powershell
$env:NVIDIA_API_KEY = "nvapi-YOUR_ACTUAL_API_KEY_HERE"
```

**Windows (Command Prompt):**
```cmd
set NVIDIA_API_KEY=nvapi-YOUR_ACTUAL_API_KEY_HERE
```

**Linux/Mac:**
```bash
export NVIDIA_API_KEY="nvapi-YOUR_ACTUAL_API_KEY_HERE"
```

### Option 3: Using Streamlit Interface

You can also enter your API key directly in the Streamlit app sidebar under "NVIDIA API Key (optional override)".

## Security Best Practices

1. **Never commit API keys to version control**
   - The `.env` file is already in `.gitignore`
   - Never paste API keys in code files

2. **Use environment variables in production**
   - Set `NVIDIA_API_KEY` as an environment variable on your server
   - Use secrets management for cloud deployments

3. **Rotate API keys regularly**
   - Generate new keys periodically
   - Revoke old keys when no longer needed

## Troubleshooting

### Error: "Authentication failed"
- ✅ Check that your API key is correct
- ✅ Ensure no extra spaces in the API key
- ✅ Verify the key hasn't expired
- ✅ Make sure you're using the right model (deepseek-ai/deepseek-v3.1)

### Error: "API key not found"
- ✅ Check that `.env` file exists in the root directory
- ✅ Verify the environment variable is set
- ✅ Restart your application after setting the API key

### Error: "Rate limit exceeded"
- ✅ Wait a few minutes before trying again
- ✅ Consider upgrading your NVIDIA account plan
- ✅ Reduce the frequency of requests

## Testing Your Setup

Run this command to test if your API key is loaded correctly:
```bash
python -c "from config import NVIDIA_API_KEY; print('API Key loaded:', NVIDIA_API_KEY[:10] + '...' if NVIDIA_API_KEY else 'Not found')"
```

You should see: `API Key loaded: nvapi-8QKs...`

## Supported Models

The application uses these NVIDIA models:
- **Chat Model**: `deepseek-ai/deepseek-v3.1`
- **Embedding Model**: `nvidia/nv-embedqa-e5-v5`

Make sure your API key has access to these models.