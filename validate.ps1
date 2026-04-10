# Pre-Submission Validation Script
# Run this before submitting to the OpenEnv hackathon

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenEnv Pre-Submission Validation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# 1. Check all required files exist
Write-Host "1. Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "inference.py",
    "openenv.yaml",
    "Dockerfile",
    "requirements.txt",
    "receipt-reconciliation/environment/env.py",
    "receipt-reconciliation/environment/models.py",
    "receipt-reconciliation/environment/tasks.py",
    "receipt-reconciliation/api/main.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MISSING" -ForegroundColor Red
        $allPassed = $false
    }
}

# 2. Verify environment variables in inference.py
Write-Host "`n2. Checking environment variables in inference.py..." -ForegroundColor Yellow
$envVars = @("API_BASE_URL", "MODEL_NAME", "HF_TOKEN")
foreach ($var in $envVars) {
    $found = Select-String -Path inference.py -Pattern $var -Quiet
    if ($found) {
        Write-Host "  ✓ $var referenced" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $var MISSING" -ForegroundColor Red
        $allPassed = $false
    }
}

# Check for defaults
Write-Host "`n   Checking defaults..." -ForegroundColor Gray
$hasAPIDefault = Select-String -Path inference.py -Pattern "router.huggingface.co" -Quiet
$hasModelDefault = Select-String -Path inference.py -Pattern "Qwen" -Quiet
if ($hasAPIDefault) {
    Write-Host "  ✓ API_BASE_URL has default" -ForegroundColor Green
} else {
    Write-Host "  ⚠ API_BASE_URL may not have default" -ForegroundColor Yellow
}
if ($hasModelDefault) {
    Write-Host "  ✓ MODEL_NAME has default" -ForegroundColor Green
} else {
    Write-Host "  ⚠ MODEL_NAME may not have default" -ForegroundColor Yellow
}

# 3. Verify OpenAI client usage
Write-Host "`n3. Checking OpenAI client usage..." -ForegroundColor Yellow
$usesOpenAI = Select-String -Path inference.py -Pattern "from openai import OpenAI" -Quiet
if ($usesOpenAI) {
    Write-Host "  ✓ Uses OpenAI client" -ForegroundColor Green
} else {
    Write-Host "  ✗ Not using OpenAI client" -ForegroundColor Red
    $allPassed = $false
}

# 4. Verify log format
Write-Host "`n4. Checking structured log format..." -ForegroundColor Yellow
$logFormats = @(
    @{Pattern = '\[START\]'; Name = "[START]"},
    @{Pattern = '\[STEP\]'; Name = "[STEP]"},
    @{Pattern = '\[END\]'; Name = "[END]"}
)
foreach ($format in $logFormats) {
    $found = Select-String -Path inference.py -Pattern $format.Pattern -Quiet
    if ($found) {
        Write-Host "  ✓ $($format.Name) format found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($format.Name) format MISSING" -ForegroundColor Red
        $allPassed = $false
    }
}

# Check for log functions
$logFunctions = @("log_start", "log_step", "log_end")
foreach ($func in $logFunctions) {
    $found = Select-String -Path inference.py -Pattern "def $func" -Quiet
    if ($found) {
        Write-Host "  ✓ ${func}() function defined" -ForegroundColor Green
    } else {
        Write-Host "  ✗ ${func}() function MISSING" -ForegroundColor Red
        $allPassed = $false
    }
}

# 5. Verify tasks
Write-Host "`n5. Checking tasks..." -ForegroundColor Yellow
try {
    $pythonCmd = "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.tasks import TASKS; tasks = list(TASKS.keys()); print(str(len(tasks)) + ' tasks: ' + ', '.join(tasks)); exit(0 if len(tasks) >= 3 else 1)"
    $taskCheck = python -c $pythonCmd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $taskCheck" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Less than 3 tasks found" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ✗ Failed to check tasks: $_" -ForegroundColor Red
    $allPassed = $false
}

# 6. Verify Pydantic models
Write-Host "`n6. Checking Pydantic models..." -ForegroundColor Yellow
try {
    python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.models import Action, Observation, Reward; print('✓ All models imported')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Action, Observation, Reward models defined" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to import models" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ✗ Failed to check models: $_" -ForegroundColor Red
    $allPassed = $false
}

# 7. Verify environment methods
Write-Host "`n7. Checking environment methods..." -ForegroundColor Yellow
try {
    python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.env import ReceiptReconciliationEnv; env = ReceiptReconciliationEnv(); assert hasattr(env, 'reset'); assert hasattr(env, 'step'); assert hasattr(env, 'state'); print('✓ All methods exist')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ reset(), step(), state() methods exist" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Missing required methods" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ✗ Failed to check methods: $_" -ForegroundColor Red
    $allPassed = $false
}

# 8. Check openenv.yaml structure
Write-Host "`n8. Checking openenv.yaml structure..." -ForegroundColor Yellow
if (Test-Path "openenv.yaml") {
    $yamlContent = Get-Content "openenv.yaml" -Raw
    $requiredFields = @("name", "tasks", "observation_space", "action_space")
    foreach ($field in $requiredFields) {
        if ($yamlContent -match $field) {
            Write-Host "  ✓ $field defined" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $field MISSING" -ForegroundColor Red
            $allPassed = $false
        }
    }
} else {
    Write-Host "  ✗ openenv.yaml not found" -ForegroundColor Red
    $allPassed = $false
}

# 9. Optional: Test Docker build
Write-Host "`n9. Docker build test (optional)..." -ForegroundColor Yellow
$response = Read-Host "Test Docker build? This may take a few minutes (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "  Building Docker image..." -ForegroundColor Gray
    docker build -t receipt-reconciliation-validation . 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Docker build successful" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Docker build failed" -ForegroundColor Red
        Write-Host "  Run 'docker build -t test .' to see detailed errors" -ForegroundColor Yellow
        $allPassed = $false
    }
} else {
    Write-Host "  ⊘ Skipped (run 'docker build -t test .' manually)" -ForegroundColor Gray
}

# 10. Optional: Test inference script
Write-Host "`n10. Inference script test (optional)..." -ForegroundColor Yellow
$response = Read-Host "Test inference script? Requires HF_TOKEN and may take time (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    if ($env:HF_TOKEN) {
        Write-Host "  Running inference script..." -ForegroundColor Gray
        Write-Host "  (This will test all 3 tasks - may take several minutes)" -ForegroundColor Gray
        $startTime = Get-Date
        python inference.py 2>&1 | Out-Null
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMinutes
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Inference completed successfully" -ForegroundColor Green
            Write-Host "  ✓ Runtime: $([math]::Round($duration, 2)) minutes" -ForegroundColor Green
            if ($duration -lt 20) {
                Write-Host "  ✓ Within 20 minute limit" -ForegroundColor Green
            } else {
                Write-Host "  ✗ Exceeds 20 minute limit" -ForegroundColor Red
                $allPassed = $false
            }
        } else {
            Write-Host "  ✗ Inference failed" -ForegroundColor Red
            $allPassed = $false
        }
    } else {
        Write-Host "  ✗ HF_TOKEN not set" -ForegroundColor Red
        Write-Host "  Set with: `$env:HF_TOKEN = 'your_token'" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⊘ Skipped" -ForegroundColor Gray
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "`n✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "`nYour project is ready for submission!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Deploy to Hugging Face Spaces" -ForegroundColor White
    Write-Host "2. Test your Space URL" -ForegroundColor White
    Write-Host "3. Submit to the hackathon" -ForegroundColor White
} else {
    Write-Host "`n⚠️  SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host "`nPlease fix the issues above before submitting." -ForegroundColor Yellow
    Write-Host "See PRE_SUBMISSION_CHECKLIST.md for details." -ForegroundColor Yellow
}

Write-Host ""
