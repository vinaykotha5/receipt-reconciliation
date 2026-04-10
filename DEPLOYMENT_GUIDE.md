# Deployment Guide - Receipt Reconciliation OpenEnv

## ✅ Validation Complete

Your project has passed all pre-submission checks:
- ✅ All required files present
- ✅ Environment variables configured
- ✅ OpenAI client usage
- ✅ Structured logging format
- ✅ 3 tasks with graders
- ✅ Pydantic models defined
- ✅ Environment methods implemented
- ✅ openenv.yaml compliant

## 🚀 Deployment to Hugging Face Spaces

### Step 1: Create Your Space

1. Go to https://huggingface.co/new-space
2. Fill in the details:
   - **Name**: `receipt-reconciliation` (or your preferred name)
   - **SDK**: Select **Docker**
   - **Hardware**: **CPU basic** (free tier)
   - **Visibility**: **Public**
3. Click "Create Space"

### Step 2: Clone Your Space Repository

```bash
# Clone the empty space
git clone https://huggingface.co/spaces/YOUR_USERNAME/receipt-reconciliation
cd receipt-reconciliation
```

Replace `YOUR_USERNAME` with your Hugging Face username.

### Step 3: Copy Your Project Files

**Option A: Using PowerShell (Windows)**
```powershell
# From your project directory
$sourceDir = "D:\vs code\meta"  # Your current project path
$targetDir = "path\to\receipt-reconciliation"  # Your cloned space path

# Copy all necessary files
Copy-Item "$sourceDir\inference.py" $targetDir
Copy-Item "$sourceDir\openenv.yaml" $targetDir
Copy-Item "$sourceDir\Dockerfile" $targetDir
Copy-Item "$sourceDir\requirements.txt" $targetDir
Copy-Item "$sourceDir\README.md" $targetDir
Copy-Item "$sourceDir\receipt-reconciliation" $targetDir -Recurse
```

**Option B: Manual Copy**
Copy these files/folders to your cloned space:
- `inference.py`
- `openenv.yaml`
- `Dockerfile`
- `requirements.txt`
- `README.md`
- `receipt-reconciliation/` (entire folder)

### Step 4: Configure Space Secrets

1. Go to your Space settings: `https://huggingface.co/spaces/YOUR_USERNAME/receipt-reconciliation/settings`
2. Scroll to "Repository secrets"
3. Click "New secret"
4. Add:
   - **Name**: `HF_TOKEN`
   - **Value**: `hf_pwQiLqLSouPjwyKcLXWXLaHlRKLsCNnMzEENV`
5. Click "Add secret"

### Step 5: Push to Hugging Face

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: Receipt Reconciliation OpenEnv environment"

# Push to HF
git push
```

### Step 6: Wait for Build

Your Space will automatically build using the Dockerfile. This typically takes 5-10 minutes.

You can monitor the build progress in the Space's "Logs" tab.

### Step 7: Test Your Deployed Space

Once the build completes and your Space is running:

```powershell
# Replace YOUR_USERNAME with your HF username
$SPACE_URL = "https://YOUR_USERNAME-receipt-reconciliation.hf.space"

# Test health endpoint
curl "$SPACE_URL/health"
# Expected: {"status":"ok","env":"receipt-reconciliation","version":"1.0.0"}

# Test tasks endpoint
curl "$SPACE_URL/tasks"
# Expected: List of 3 tasks

# Test reset endpoint
curl -X POST "$SPACE_URL/reset" -H "Content-Type: application/json" -d '{\"task_id\":\"task_easy\"}'
# Expected: Initial observation JSON
```

## 📝 Submission to Hackathon

Once your Space is deployed and tested:

1. **Verify Space is Running**
   - Visit your Space URL
   - Check that it returns 200 status
   - Test the /reset endpoint

2. **Submit Your Entry**
   - Go to the hackathon submission page
   - Provide your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/receipt-reconciliation`
   - Provide your inference.py (already in your Space repo)

3. **Wait for Validation**
   - The hackathon system will automatically validate your submission
   - It will check:
     - Space accessibility
     - OpenEnv compliance
     - Docker build
     - Inference script execution
     - Task graders

## 🔧 Troubleshooting

### Space Build Fails

**Check the logs:**
1. Go to your Space
2. Click "Logs" tab
3. Look for error messages

**Common issues:**
- Missing dependencies in requirements.txt
- Dockerfile syntax errors
- Port configuration issues

**Solution:**
```bash
# Test Docker build locally first
docker build -t test .
docker run -p 7860:7860 -e HF_TOKEN=your_token test
```

### Space Returns 500 Error

**Possible causes:**
- HF_TOKEN not set in Space secrets
- Import errors in Python code
- Missing environment files

**Solution:**
1. Check Space logs for Python errors
2. Verify HF_TOKEN is set in secrets
3. Test locally with same environment

### Inference Script Fails

**Check:**
- API_BASE_URL is accessible
- HF_TOKEN has correct permissions
- Model name is valid

**Test locally:**
```powershell
$env:HF_TOKEN = "your_token"
python inference.py
```

### Space Not Responding

**Wait time:**
- Initial build: 5-10 minutes
- Cold start: 30-60 seconds

**If still not responding:**
1. Check Space status (should show "Running")
2. Restart the Space
3. Check logs for errors

## 📊 Expected Performance

Your Receipt Reconciliation environment should:
- **Build time**: 5-10 minutes
- **Cold start**: 30-60 seconds
- **Inference time**: 2-5 minutes per task
- **Total runtime**: < 20 minutes for all 3 tasks

## 🎯 Validation Checklist

Before submitting, verify:
- [ ] Space is publicly accessible
- [ ] Health endpoint returns 200
- [ ] Reset endpoint works
- [ ] All 3 tasks are accessible
- [ ] Graders return scores 0.0-1.0
- [ ] Inference script completes without errors
- [ ] Structured logs are correct format
- [ ] Runtime < 20 minutes

## 🆘 Getting Help

If you encounter issues:
1. Check Space logs first
2. Test locally with Docker
3. Review PRE_SUBMISSION_CHECKLIST.md
4. Check OpenEnv documentation: https://github.com/meta-pytorch/OpenEnv

## 🎉 Success!

Once your Space is running and validated, you're done!

Your Receipt Reconciliation environment is:
- ✅ Deployed to Hugging Face Spaces
- ✅ OpenEnv compliant
- ✅ Ready for hackathon evaluation
- ✅ Publicly accessible

Good luck with the hackathon! 🚀
