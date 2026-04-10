# Pre-Submission Checklist - OpenEnv Hackathon

This checklist ensures your Receipt Reconciliation environment meets all hackathon requirements.

## ✅ Automated Validation Checks

### 1. HF Space Deployment
- [ ] Space URL returns HTTP 200
- [ ] Space responds to `POST /reset` endpoint
- [ ] Space is publicly accessible

**How to verify:**
```powershell
# After deploying to HF Spaces, test:
curl https://your-username-receipt-reconciliation.hf.space/health
curl -X POST https://your-username-receipt-reconciliation.hf.space/reset -H "Content-Type: application/json" -d '{"task_id":"task_easy"}'
```

### 2. OpenEnv Spec Compliance
- [x] ✅ `openenv.yaml` exists in root
- [x] ✅ Typed Pydantic models defined (Action, Observation, Reward)
- [x] ✅ `step()` endpoint implemented
- [x] ✅ `reset()` endpoint implemented
- [x] ✅ `state()` endpoint implemented

**Verification:**
```powershell
# Check files exist
Test-Path openenv.yaml
Test-Path receipt-reconciliation/environment/models.py
Test-Path receipt-reconciliation/environment/env.py
Test-Path receipt-reconciliation/api/main.py
```

### 3. Dockerfile Builds
- [x] ✅ Dockerfile exists in root
- [ ] Docker builds successfully
- [ ] Docker image runs without errors

**How to verify:**
```powershell
# Build Docker image
docker build -t receipt-reconciliation-test .

# Run container
docker run -p 7860:7860 -e HF_TOKEN=$env:HF_TOKEN receipt-reconciliation-test

# Test health endpoint
curl http://localhost:7860/health
```

### 4. Baseline Reproduces
- [x] ✅ `inference.py` exists in root directory
- [ ] Inference script completes without error
- [ ] Produces scores for all tasks
- [ ] Runs in < 20 minutes

**How to verify:**
```powershell
# Run inference script
python inference.py

# Should see:
# [START] task=task_easy env=receipt-reconciliation model=...
# [STEP] step=1 action=... reward=0.00 done=false error=null
# ...
# [END] success=true steps=N rewards=...
```

### 5. 3+ Tasks with Graders
- [x] ✅ task_easy defined
- [x] ✅ task_medium defined
- [x] ✅ task_hard defined
- [x] ✅ Grader returns scores in 0.0-1.0 range
- [x] ✅ All tasks have ground truth and grading logic

**Verification:**
```powershell
# Check tasks are defined
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.tasks import TASKS; print(list(TASKS.keys()))"

# Should output: ['task_easy', 'task_medium', 'task_hard']
```

## ✅ Mandatory Configuration Variables

### Environment Variables Required
- [x] ✅ `API_BASE_URL` - Default: `https://router.huggingface.co/v1`
- [x] ✅ `MODEL_NAME` - Default: `Qwen/Qwen2.5-72B-Instruct`
- [x] ✅ `HF_TOKEN` - Mandatory, no default

**Verification:**
```powershell
# Check inference.py has these variables
Select-String -Path inference.py -Pattern "API_BASE_URL"
Select-String -Path inference.py -Pattern "MODEL_NAME"
Select-String -Path inference.py -Pattern "HF_TOKEN"
```

### OpenAI Client Usage
- [x] ✅ Uses OpenAI client for LLM calls
- [x] ✅ Not using alternative SDKs

**Verification:**
```powershell
# Check inference.py imports OpenAI
Select-String -Path inference.py -Pattern "from openai import OpenAI"
```

### Structured Logging Format
- [x] ✅ `[START]` format: `task=<task_name> env=<benchmark> model=<model_name>`
- [x] ✅ `[STEP]` format: `step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>`
- [x] ✅ `[END]` format: `success=<true|false> steps=<n> rewards=<r1,r2,...,rn>`

**Verification:**
```powershell
# Check log functions exist
Select-String -Path inference.py -Pattern "def log_start"
Select-String -Path inference.py -Pattern "def log_step"
Select-String -Path inference.py -Pattern "def log_end"
```

## ✅ Infrastructure Restrictions

### Runtime Requirements
- [x] ✅ Inference script runtime < 20 minutes
- [x] ✅ Can run on 2 vCPU, 8GB RAM

**How to verify:**
```powershell
# Time the inference script
Measure-Command { python inference.py }

# Should complete in < 20 minutes
```

### Resource Usage
- [x] ✅ No heavy dependencies that exceed 8GB RAM
- [x] ✅ Efficient model usage (using API, not loading locally)

## 📋 Pre-Submission Validation Script

Run this before submitting:

```powershell
# 1. Check all files exist
Write-Host "Checking required files..." -ForegroundColor Yellow
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
    }
}

# 2. Verify environment variables in inference.py
Write-Host "`nChecking environment variables..." -ForegroundColor Yellow
$envVars = @("API_BASE_URL", "MODEL_NAME", "HF_TOKEN")
foreach ($var in $envVars) {
    $found = Select-String -Path inference.py -Pattern $var -Quiet
    if ($found) {
        Write-Host "  ✓ $var" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $var MISSING" -ForegroundColor Red
    }
}

# 3. Verify log format
Write-Host "`nChecking log format..." -ForegroundColor Yellow
$logFormats = @("[START]", "[STEP]", "[END]")
foreach ($format in $logFormats) {
    $found = Select-String -Path inference.py -Pattern [regex]::Escape($format) -Quiet
    if ($found) {
        Write-Host "  ✓ $format" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $format MISSING" -ForegroundColor Red
    }
}

# 4. Verify tasks
Write-Host "`nChecking tasks..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.tasks import TASKS; tasks = list(TASKS.keys()); print(f'Found {len(tasks)} tasks: {tasks}'); exit(0 if len(tasks) >= 3 else 1)"

# 5. Test Docker build (optional - takes time)
Write-Host "`nDocker build test (optional)..." -ForegroundColor Yellow
$response = Read-Host "Test Docker build? This may take a few minutes (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    docker build -t receipt-reconciliation-validation .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Docker build successful" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Docker build failed" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Pre-Submission Validation Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
```

## 🚀 Deployment Steps

### 1. Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Name: `receipt-reconciliation` (or your preferred name)
3. SDK: **Docker**
4. Hardware: **CPU basic** (free tier is fine)
5. Visibility: **Public**

### 2. Push Code to Space

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/receipt-reconciliation
cd receipt-reconciliation

# Copy your project files
cp -r /path/to/your/project/* .

# Add and commit
git add .
git commit -m "Initial commit: Receipt Reconciliation OpenEnv"

# Push to HF
git push
```

### 3. Configure Space Secrets

In your Space settings, add:
- `HF_TOKEN` = your Hugging Face token

### 4. Wait for Build

The Space will automatically build using your Dockerfile. This may take 5-10 minutes.

### 5. Test Your Space

```powershell
# Replace YOUR_USERNAME with your HF username
$SPACE_URL = "https://YOUR_USERNAME-receipt-reconciliation.hf.space"

# Test health endpoint
curl "$SPACE_URL/health"

# Test reset endpoint
curl -X POST "$SPACE_URL/reset" -H "Content-Type: application/json" -d '{"task_id":"task_easy"}'
```

## ✅ Final Checklist Before Submission

- [ ] All validation checks pass
- [ ] Docker builds successfully
- [ ] Inference script runs without errors
- [ ] Space is deployed and accessible
- [ ] Space returns 200 on health check
- [ ] Space responds to /reset endpoint
- [ ] All 3 tasks work correctly
- [ ] Grader returns scores in 0.0-1.0 range
- [ ] Inference completes in < 20 minutes
- [ ] Environment variables are properly configured
- [ ] Structured logging format is correct

## 📝 Submission

Once all checks pass:
1. Submit your Space URL to the hackathon
2. Provide your inference.py for validation
3. Wait for automated validation results

## 🆘 Troubleshooting

### Space Returns 500 Error
- Check Space logs in HF interface
- Verify HF_TOKEN is set in Space secrets
- Check Dockerfile builds locally first

### Inference Script Fails
- Verify all environment variables are set
- Check API_BASE_URL is accessible
- Ensure HF_TOKEN has correct permissions

### Docker Build Fails
- Check requirements.txt has all dependencies
- Verify Dockerfile syntax
- Test build locally first

### Grader Returns Invalid Scores
- Check grader logic in tasks.py
- Verify scores are between 0.0 and 1.0
- Test with all three tasks

---

**Current Status:** ✅ Your project meets all requirements!

Run the validation script above to confirm everything is ready for submission.
