# Quick Start Script - Sets environment variables and runs setup
# This script loads .env file and sets up everything

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Receipt Reconciliation - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with your HF_TOKEN" -ForegroundColor Yellow
    Write-Host "See .env.example for template" -ForegroundColor Yellow
    exit 1
}

# Load environment variables from .env
Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
        Write-Host "  ✓ Set $name" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Environment variables loaded!" -ForegroundColor Green
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Running setup..." -ForegroundColor Yellow
    & .\setup.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Setup failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    Write-Host "Activating..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ready to go!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose an option:" -ForegroundColor Yellow
Write-Host "1. Run inference script (test the agent)" -ForegroundColor White
Write-Host "2. Start API server" -ForegroundColor White
Write-Host "3. Run tests" -ForegroundColor White
Write-Host "4. Build Docker image" -ForegroundColor White
Write-Host "5. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running inference script..." -ForegroundColor Cyan
        Write-Host "This will test the agent on all three tasks" -ForegroundColor Yellow
        Write-Host ""
        python inference.py
    }
    "2" {
        Write-Host ""
        Write-Host "Starting API server on port 7860..." -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        Set-Location receipt-reconciliation
        python -m uvicorn api.main:app --host 0.0.0.0 --port 7860 --reload
    }
    "3" {
        Write-Host ""
        Write-Host "Running tests..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Bug Condition Tests:" -ForegroundColor Yellow
        python test_bug_condition.py
        Write-Host ""
        Write-Host "Preservation Tests:" -ForegroundColor Yellow
        python test_preservation.py
    }
    "4" {
        Write-Host ""
        Write-Host "Building Docker image..." -ForegroundColor Cyan
        docker build -t receipt-reconciliation .
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "To run the container:" -ForegroundColor Yellow
            Write-Host "  docker run -p 7860:7860 -e HF_TOKEN=$env:HF_TOKEN receipt-reconciliation" -ForegroundColor White
        }
    }
    "5" {
        Write-Host "Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
    }
}
