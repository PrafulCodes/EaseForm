# Backend Venv Recreation Script
# Run this from the backend directory

Write-Host "🔧 Recreating Backend Virtual Environment..." -ForegroundColor Cyan

# Step 1: Deactivate current venv (if active)
Write-Host "`n1. Deactivating current venv..." -ForegroundColor Yellow
deactivate 2>$null

# Step 2: Remove old venv
Write-Host "`n2. Removing old venv directory..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Remove-Item -Recurse -Force venv
    Write-Host "   ✅ Old venv removed" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No existing venv found" -ForegroundColor Gray
}

# Step 3: Create new venv with Python 3.11
Write-Host "`n3. Creating new venv with Python 3.11..." -ForegroundColor Yellow
py -3.11 -m venv venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Venv created successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to create venv. Make sure Python 3.11 is installed." -ForegroundColor Red
    exit 1
}

# Step 4: Activate venv
Write-Host "`n4. Activating venv..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "   ✅ Venv activated" -ForegroundColor Green

# Step 5: Verify Python version
Write-Host "`n5. Verifying Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "   $pythonVersion" -ForegroundColor Cyan

# Step 6: Upgrade pip
Write-Host "`n6. Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✅ Pip upgraded" -ForegroundColor Green

# Step 7: Clear pip cache
Write-Host "`n7. Clearing pip cache..." -ForegroundColor Yellow
pip cache purge | Out-Null
Write-Host "   ✅ Cache cleared" -ForegroundColor Green

# Step 8: Install dependencies
Write-Host "`n8. Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --no-cache-dir
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 9: Verify httpx version
Write-Host "`n9. Verifying httpx version..." -ForegroundColor Yellow
pip show httpx | Select-String "Version:"

# Step 10: Test app import
Write-Host "`n10. Testing app import..." -ForegroundColor Yellow
python -c "from app.main import app; print('✅ OK')"

Write-Host "`n✅ Setup complete! Start backend with:" -ForegroundColor Green
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Cyan
