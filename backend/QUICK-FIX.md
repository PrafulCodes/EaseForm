# 🔧 Quick Fix Guide - Supabase Proxy Error

## The Error
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxy'
```

## The Fix (2 Steps)

### Step 1: Stop Backend Server
Press `Ctrl+C` in the terminal running uvicorn

### Step 2: Run Fix Script
```powershell
cd backend
.\fix-supabase-deps.ps1
```

That's it! The script will:
- ✅ Uninstall old packages
- ✅ Install compatible versions
- ✅ Test everything works
- ✅ Show you when it's ready

### Step 3: Restart Server
```powershell
uvicorn app.main:app --reload
```

---

## What Was Fixed

| Package | Old Version | New Version |
|---------|-------------|-------------|
| supabase | 2.3.4 | 2.10.0 ✅ |
| gotrue | 2.9.0+ (standalone) | Removed (bundled) ✅ |
| httpx | 0.24-0.26 | 0.27.2 ✅ |

---

## Manual Commands (if script fails)

```powershell
# 1. Activate venv
.\venv\Scripts\Activate.ps1

# 2. Uninstall old packages
pip uninstall -y supabase gotrue httpx postgrest realtime storage3 supafunc

# 3. Clear cache
pip cache purge

# 4. Install fixed versions
pip install -r requirements.txt --no-cache-dir

# 5. Test it works
python -c "from app.utils.supabase import get_supabase_client; print('✅ Fixed!')"

# 6. Start server
uvicorn app.main:app --reload
```

---

## Why This Happened

- `supabase 2.3.4` was too old
- `gotrue 2.9.1` added proxy support
- They became incompatible → TypeError
- **Fix:** Upgrade to `supabase 2.10.0` (includes proxy support)

---

## Need Help?

See the full walkthrough for detailed explanation and troubleshooting.
