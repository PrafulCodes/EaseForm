# Backend Setup Guide

## Python Version Requirement

**Required:** Python 3.11.x  
**Not Supported:** Python 3.13

## Quick Start (Windows)

```bash
# 1. Check Python version
python --version  # Must be 3.11.x

# 2. Navigate to backend
cd backend

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Configure environment
copy .env.example .env
# Edit .env with your Supabase credentials

# 7. Run server
uvicorn app.main:app --reload
```

## Troubleshooting

### Using Python 3.13?

Dependencies like `pydantic-core` don't have pre-built wheels for Python 3.13 yet.

**Fix:** Install Python 3.11 and create a new virtual environment:

```bash
# Download Python 3.11 from python.org
# Then create venv with Python 3.11
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### pip install hanging?

If stuck on "Preparing metadata (pyproject.toml)", you're likely on Python 3.13.

**Solution:** Use Python 3.11 (see above).

### ModuleNotFoundError?

Make sure virtual environment is activated:

```bash
venv\Scripts\activate
# You should see (venv) in your prompt
```

## Verify Installation

```bash
# Check installed packages
pip list

# Test server
uvicorn app.main:app --reload

# Visit http://localhost:8000/health
# Should return: {"status":"healthy",...}
```
