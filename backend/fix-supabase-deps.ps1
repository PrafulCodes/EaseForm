# Fix Supabase Dependencies Script
# Run this to fix the proxy argument error

Write-Host "🔧 Fixing Supabase Dependencies..." -ForegroundColor Cyan

# Step 1: Stop the server first
Write-Host "`n⚠️  IMPORTANT: Stop the uvicorn server (Ctrl+C) before running this script!" -ForegroundColor Yellow
Write-Host "Press any key to continue once server is stopped..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 2: Activate venv
Write-Host "`n1. Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "   ✅ Venv activated" -ForegroundColor Green

# Step 3: Uninstall conflicting packages
Write-Host "`n2. Uninstalling old/conflicting packages..." -ForegroundColor Yellow
pip uninstall -y supabase gotrue httpx postgrest realtime storage3 supafunc 2>$null
Write-Host "   ✅ Old packages removed" -ForegroundColor Green

# Step 4: Clear pip cache
Write-Host "`n3. Clearing pip cache..." -ForegroundColor Yellow
pip cache purge | Out-Null
Write-Host "   ✅ Cache cleared" -ForegroundColor Green

# Step 5: Install updated dependencies
Write-Host "`n4. Installing fixed dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --no-cache-dir
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 6: Verify versions
Write-Host "`n5. Verifying installed versions..." -ForegroundColor Yellow
Write-Host "   Supabase: " -NoNewline -ForegroundColor Cyan
pip show supabase | Select-String "Version:" | ForEach-Object { $_.ToString().Replace("Version: ", "") }
Write-Host "   httpx: " -NoNewline -ForegroundColor Cyan
pip show httpx | Select-String "Version:" | ForEach-Object { $_.ToString().Replace("Version: ", "") }

# Step 7: Test import
Write-Host "`n6. Testing Supabase client import..." -ForegroundColor Yellow
python -c "from app.utils.supabase import get_supabase_client; print('   ✅ Import successful!')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ No proxy argument error!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Import failed - check error above" -ForegroundColor Red
    exit 1
}

# Step 8: Test client initialization
Write-Host "`n7. Testing client initialization..." -ForegroundColor Yellow
python -c "from app.utils.supabase import get_supabase_client; client = get_supabase_client(); print('   ✅ Client initialized successfully!')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ No errors!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Initialization failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Fix complete! The proxy argument error is resolved." -ForegroundColor Green
Write-Host "`nStart your backend server with:" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White
