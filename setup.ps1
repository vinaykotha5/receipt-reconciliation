# OpenEnv Receipt Reconciliation - Setup Script (PowerShell)
# This script sets up the virtual environment and installs all dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenEnv Receipt Reconciliation Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if venv already exists
if (Test-Path "venv") {
    Write-Host ""
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
    $response = Read-Host "Do you want to recreate it? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Removing existing venv..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv
    } else {
        Write-Host "Using existing venv..." -ForegroundColor Green
        Write-Host ""
        Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
        Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
        exit 0
    }
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Virtual environment created" -ForegroundColor Green

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Optional: Install openenv-core
Write-Host ""
$response = Read-Host "Install openenv-core CLI tools? (Y/n)"
if ($response -ne "n" -and $response -ne "N") {
    Write-Host "Installing openenv-core..." -ForegroundColor Yellow
    pip install openenv-core --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ openenv-core installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install openenv-core (optional)" -ForegroundColor Yellow
    }
}

# Test imports
Write-Host ""
Write-Host "Testing imports..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.env import ReceiptReconciliationEnv; print('✓ Imports work!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Environment setup complete!" -ForegroundColor Green
} else {
    Write-Host "✗ Import test failed" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set your Hugging Face token:" -ForegroundColor White
Write-Host "   `$env:HF_TOKEN='your_token_here'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run the inference script:" -ForegroundColor White
Write-Host "   python inference.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Or start the API server:" -ForegroundColor White
Write-Host "   cd receipt-reconciliation" -ForegroundColor Gray
Write-Host "   uvicorn api.main:app --host 0.0.0.0 --port 7860" -ForegroundColor Gray
Write-Host ""
Write-Host "To activate the virtual environment later:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
