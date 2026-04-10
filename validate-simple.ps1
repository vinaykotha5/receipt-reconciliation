# Simple Pre-Submission Validation Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenEnv Pre-Submission Validation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# 1. Check required files
Write-Host "1. Checking required files..." -ForegroundColor Yellow
$files = @(
    "inference.py",
    "openenv.yaml",
    "Dockerfile",
    "requirements.txt"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  OK $file" -ForegroundColor Green
    } else {
        Write-Host "  FAIL $file MISSING" -ForegroundColor Red
        $allPassed = $false
    }
}

# 2. Check environment variables
Write-Host "`n2. Checking environment variables..." -ForegroundColor Yellow
$content = Get-Content inference.py -Raw
if ($content -match "API_BASE_URL") {
    Write-Host "  OK API_BASE_URL" -ForegroundColor Green
} else {
    Write-Host "  FAIL API_BASE_URL missing" -ForegroundColor Red
    $allPassed = $false
}

if ($content -match "MODEL_NAME") {
    Write-Host "  OK MODEL_NAME" -ForegroundColor Green
} else {
    Write-Host "  FAIL MODEL_NAME missing" -ForegroundColor Red
    $allPassed = $false
}

if ($content -match "HF_TOKEN") {
    Write-Host "  OK HF_TOKEN" -ForegroundColor Green
} else {
    Write-Host "  FAIL HF_TOKEN missing" -ForegroundColor Red
    $allPassed = $false
}

# 3. Check OpenAI client
Write-Host "`n3. Checking OpenAI client..." -ForegroundColor Yellow
if ($content -match "from openai import OpenAI") {
    Write-Host "  OK Uses OpenAI client" -ForegroundColor Green
} else {
    Write-Host "  FAIL Not using OpenAI client" -ForegroundColor Red
    $allPassed = $false
}

# 4. Check log format
Write-Host "`n4. Checking log format..." -ForegroundColor Yellow
if ($content -match "\[START\]") {
    Write-Host "  OK [START] format" -ForegroundColor Green
} else {
    Write-Host "  FAIL [START] missing" -ForegroundColor Red
    $allPassed = $false
}

if ($content -match "\[STEP\]") {
    Write-Host "  OK [STEP] format" -ForegroundColor Green
} else {
    Write-Host "  FAIL [STEP] missing" -ForegroundColor Red
    $allPassed = $false
}

if ($content -match "\[END\]") {
    Write-Host "  OK [END] format" -ForegroundColor Green
} else {
    Write-Host "  FAIL [END] missing" -ForegroundColor Red
    $allPassed = $false
}

# 5. Check tasks
Write-Host "`n5. Checking tasks..." -ForegroundColor Yellow
Write-Host "  Running Python check..." -ForegroundColor Gray
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.tasks import TASKS; print('  OK Found', len(TASKS), 'tasks:', list(TASKS.keys())); exit(0 if len(TASKS) >= 3 else 1)"
if ($LASTEXITCODE -eq 0) {
    # Success message already printed by Python
} else {
    Write-Host "  FAIL Less than 3 tasks" -ForegroundColor Red
    $allPassed = $false
}

# 6. Check models
Write-Host "`n6. Checking Pydantic models..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.models import Action, Observation, Reward; print('  OK All models imported')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  FAIL Failed to import models" -ForegroundColor Red
    $allPassed = $false
}

# 7. Check environment methods
Write-Host "`n7. Checking environment methods..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.env import ReceiptReconciliationEnv; env = ReceiptReconciliationEnv(); assert hasattr(env, 'reset'); assert hasattr(env, 'step'); assert hasattr(env, 'state'); print('  OK reset(), step(), state() exist')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  FAIL Missing required methods" -ForegroundColor Red
    $allPassed = $false
}

# 8. Check openenv.yaml
Write-Host "`n8. Checking openenv.yaml..." -ForegroundColor Yellow
$yaml = Get-Content openenv.yaml -Raw
$fields = @("name", "tasks", "observation_space", "action_space")
foreach ($field in $fields) {
    if ($yaml -match $field) {
        Write-Host "  OK $field" -ForegroundColor Green
    } else {
        Write-Host "  FAIL $field missing" -ForegroundColor Red
        $allPassed = $false
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nYour project is ready for submission!" -ForegroundColor Green
} else {
    Write-Host "SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nPlease fix the issues above." -ForegroundColor Yellow
}
Write-Host ""
