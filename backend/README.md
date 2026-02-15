# EaseForm Backend - FastAPI + Supabase

Production-grade Python backend for EaseForm form builder.

## Architecture

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth (Google OAuth)
- **Realtime**: Supabase Realtime

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration & environment
│   ├── dependencies.py      # Auth dependencies
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── form.py
│   │   ├── response.py
│   │   └── host.py
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   ├── responses.py
│   │   └── hosts.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── form_service.py
│   │   ├── response_service.py
│   │   └── device_service.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── supabase.py
│       └── security.py
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

> **⚠️ IMPORTANT: Python 3.11 is required**
> 
> Python 3.13 is **NOT supported** due to missing pre-built wheels for dependencies like `pydantic-core`.
> 
> **Supported Python versions:** 3.11.x

## Setup

### 1. Verify Python Version

```bash
python --version
# Should show: Python 3.11.x
```

If you have Python 3.13, you need to install Python 3.11:
- Download from [python.org](https://www.python.org/downloads/)
- Or use `pyenv` to manage multiple Python versions

### 2. Create Virtual Environment (Windows)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with Python 3.11
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify you're using the venv
where python
# Should show: ...\backend\venv\Scripts\python.exe
```

### 3. Install Dependencies

```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

This should complete in 1-2 minutes without compilation.

### 4. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env with your Supabase credentials
notepad .env
```

### 5. Run Server

```bash
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

## API Endpoints

### Forms
- `POST /api/forms` - Create form (authenticated)
- `GET /api/forms` - List user's forms (authenticated)
- `GET /api/forms/{form_id}` - Get form details
- `PUT /api/forms/{form_id}` - Update form (authenticated)
- `DELETE /api/forms/{form_id}` - Delete form (authenticated)

### Responses
- `POST /api/forms/{form_id}/responses` - Submit response (public)
- `GET /api/forms/{form_id}/responses` - Get responses (authenticated, owner only)
- `DELETE /api/responses/{response_id}` - Delete response (authenticated, owner only)

### Hosts
- `GET /api/hosts/me` - Get current user profile (authenticated)
- `PUT /api/hosts/me` - Update profile (authenticated)

## Security

- JWT validation via Supabase
- Row Level Security (RLS) enforced at database
- Device fingerprinting for response deduplication
- CORS configured for frontend origin

## Troubleshooting

### Python 3.13 Compatibility

If you see errors like:
```
Building wheel for pydantic-core (pyproject.toml) ... error
```

Or pip hangs on:
```
Preparing metadata (pyproject.toml) ...
```

**Solution:** You're using Python 3.13. Switch to Python 3.11:

1. Install Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Create a new virtual environment:
   ```bash
   # Use Python 3.11 explicitly
   py -3.11 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Virtual Environment Not Activated

If you see `ModuleNotFoundError` when running uvicorn:
```bash
# Make sure venv is activated (you should see (venv) in prompt)
venv\Scripts\activate
```

### Port Already in Use

If port 8000 is already in use:
```bash
uvicorn app.main:app --reload --port 8001
```

## Environment Variables

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
FRONTEND_URL=http://localhost:3000
```
