# Full Manual Test Script for Receipt Reconciliation OpenEnv

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Full Manual Test - Receipt Reconciliation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Test 1: Check Docker is available
Write-Host "Test 1: Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  OK Docker installed: $dockerVersion" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "  FAIL Docker not installed" -ForegroundColor Red
    $testsFailed++
}

# Test 2: Check Docker daemon
Write-Host "`nTest 2: Checking Docker daemon..." -ForegroundColor Yellow
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Docker daemon is running" -ForegroundColor Green
    $testsPassed++
    $dockerAvailable = $true
} else {
    Write-Host "  FAIL Docker daemon is not running" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again" -ForegroundColor Yellow
    $testsFailed++
    $dockerAvailable = $false
}

# Test 3: Check required files
Write-Host "`nTest 3: Checking required files..." -ForegroundColor Yellow
$requiredFiles = @("Dockerfile", "inference.py", "openenv.yaml", "requirements.txt")
$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  OK $file" -ForegroundColor Green
    } else {
        Write-Host "  FAIL $file missing" -ForegroundColor Red
        $allFilesExist = $false
    }
}
if ($allFilesExist) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 4: Check environment variables
Write-Host "`nTest 4: Checking environment variables..." -ForegroundColor Yellow
if ($env:HF_TOKEN) {
    Write-Host "  OK HF_TOKEN is set" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  WARN HF_TOKEN not set (needed for inference test)" -ForegroundColor Yellow
    Write-Host "  Set with: `$env:HF_TOKEN = 'your_token'" -ForegroundColor Gray
    $testsFailed++
}

# Test 5: Docker build (if Docker is available)
if ($dockerAvailable) {
    Write-Host "`nTest 5: Building Docker image..." -ForegroundColor Yellow
    Write-Host "  This may take 5-10 minutes..." -ForegroundColor Gray
    
    $buildStart = Get-Date
    docker build -t receipt-reconciliation-test . 2>&1 | Out-Null
    $buildEnd = Get-Date
    $buildTime = ($buildEnd - $buildStart).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Docker build successful (${buildTime}s)" -ForegroundColor Green
        $testsPassed++
        $dockerBuilt = $true
    } else {
        Write-Host "  FAIL Docker build failed" -ForegroundColor Red
        Write-Host "  Run 'docker build -t test .' to see detailed errors" -ForegroundColor Yellow
        $testsFailed++
        $dockerBuilt = $false
    }
} else {
    Write-Host "`nTest 5: Docker build - SKIPPED (Docker not available)" -ForegroundColor Gray
    $dockerBuilt = $false
}

# Test 6: Docker run (if build succeeded)
if ($dockerBuilt) {
    Write-Host "`nTest 6: Running Docker container..." -ForegroundColor Yellow
    Write-Host "  Starting container on port 7860..." -ForegroundColor Gray
    
    # Start container in background
    $containerId = docker run -d -p 7860:7860 -e HF_TOKEN=$env:HF_TOKEN receipt-reconciliation-test 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Container started: $containerId" -ForegroundColor Green
        
        # Wait for container to be ready
        Write-Host "  Waiting for container to be ready..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
        
        # Test 7: Health endpoint
        Write-Host "`nTest 7: Testing /health endpoint..." -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:7860/health" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Host "  OK Health endpoint returned 200" -ForegroundColor Green
                Write-Host "  Response: $($response.Content)" -ForegroundColor Gray
                $testsPassed++
            } else {
                Write-Host "  FAIL Health endpoint returned $($response.StatusCode)" -ForegroundColor Red
                $testsFailed++
            }
        } catch {
            Write-Host "  FAIL Could not reach health endpoint: $_" -ForegroundColor Red
            $testsFailed++
        }
        
        # Test 8: Tasks endpoint
        Write-Host "`nTest 8: Testing /tasks endpoint..." -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:7860/tasks" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Host "  OK Tasks endpoint returned 200" -ForegroundColor Green
                $tasks = $response.Content | ConvertFrom-Json
                Write-Host "  Found $($tasks.tasks.Count) tasks" -ForegroundColor Gray
                $testsPassed++
            } else {
                Write-Host "  FAIL Tasks endpoint returned $($response.StatusCode)" -ForegroundColor Red
                $testsFailed++
            }
        } catch {
            Write-Host "  FAIL Could not reach tasks endpoint: $_" -ForegroundColor Red
            $testsFailed++
        }
        
        # Test 9: Reset endpoint
        Write-Host "`nTest 9: Testing /reset endpoint..." -ForegroundColor Yellow
        try {
            $body = @{task_id = "task_easy"} | ConvertTo-Json
            $response = Invoke-WebRequest -Uri "http://localhost:7860/reset" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Host "  OK Reset endpoint returned 200" -ForegroundColor Green
                $testsPassed++
            } else {
                Write-Host "  FAIL Reset endpoint returned $($response.StatusCode)" -ForegroundColor Red
                $testsFailed++
            }
        } catch {
            Write-Host "  FAIL Could not reach reset endpoint: $_" -ForegroundColor Red
            $testsFailed++
        }
        
        # Stop container
        Write-Host "`nStopping container..." -ForegroundColor Gray
        docker stop $containerId 2>&1 | Out-Null
        docker rm $containerId 2>&1 | Out-Null
        Write-Host "  Container stopped and removed" -ForegroundColor Gray
        
    } else {
        Write-Host "  FAIL Could not start container" -ForegroundColor Red
        $testsFailed++
    }
} else {
    Write-Host "`nTest 6-9: Docker tests - SKIPPED (Docker not available or build failed)" -ForegroundColor Gray
}

# Test 10: Python imports
Write-Host "`nTest 10: Testing Python imports..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.env import ReceiptReconciliationEnv; from environment.models import Action, Observation, Reward; print('  OK All imports successful')" 2>&1
if ($LASTEXITCODE -eq 0) {
    $testsPassed++
} else {
    Write-Host "  FAIL Import test failed" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Your project is ready for deployment!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Please review the errors above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If Docker tests were skipped, start Docker Desktop" -ForegroundColor White
Write-Host "2. Deploy to Hugging Face Spaces (see DEPLOYMENT_GUIDE.md)" -ForegroundColor White
Write-Host "3. Submit to hackathon" -ForegroundColor White
Write-Host ""
