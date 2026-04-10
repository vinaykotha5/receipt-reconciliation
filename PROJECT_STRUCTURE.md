# Project Structure - Receipt Reconciliation OpenEnv

## ✅ Correct Structure (OpenEnv Compliant)

```
root/ (outermost/main folder)
│
├── Dockerfile                    ← ONE Dockerfile here (not in server folder)
├── inference.py                  ← Baseline agent (OpenEnv requirement)
├── openenv.yaml                  ← Environment metadata
├── requirements.txt              ← Python dependencies
├── README.md                     ← Project documentation
├── .env                          ← Environment variables (local)
├── .gitignore                    ← Git ignore rules
│
├── setup.ps1                     ← Setup scripts
├── quick-start.ps1               ← Quick start menu
├── validate-simple.ps1           ← Validation script
│
├── SETUP_GUIDE.md                ← Documentation
├── DEPLOYMENT_GUIDE.md
├── PRE_SUBMISSION_CHECKLIST.md
├── PROJECT_SUMMARY.md
├── PROJECT_STRUCTURE.md          ← This file
│
└── receipt-reconciliation/       ← "Server" folder (environment implementation)
    ├── environment/              ← Core environment package
    │   ├── __init__.py
    │   ├── env.py               ← Environment logic (reset/step/state)
    │   ├── models.py            ← Pydantic models
    │   └── tasks.py             ← Task definitions and graders
    │
    ├── api/                     ← API server (FastAPI)
    │   ├── __init__.py
    │   └── main.py              ← API endpoints (/health, /reset, /step, /state)
    │
    ├── app.py                   ← HF Spaces entrypoint
    ├── openenv.yaml             ← Environment metadata (copy)
    ├── README.md                ← Full documentation
    └── requirements.txt         ← Dependencies (copy)
```

## 📋 Key Points

### 1. ONE Dockerfile in Root
- ✅ `Dockerfile` is in the **root** (outermost folder)
- ❌ No Dockerfile in `receipt-reconciliation/` folder
- This follows OpenEnv guidelines: "move the Dockerfile to the outermost (main) folder"

### 2. What is the "Server"?
The **"server"** refers to the environment API server:
- Located in: `receipt-reconciliation/api/`
- Contains: FastAPI application that exposes the environment over HTTP
- Endpoints: `/health`, `/tasks`, `/reset`, `/step`, `/state`

### 3. How Docker Works
When you run `docker build .` from root:
1. Docker uses the root `Dockerfile`
2. Copies all files (including `receipt-reconciliation/`)
3. Installs dependencies from root `requirements.txt`
4. Starts the API server with: `uvicorn receipt-reconciliation.api.main:app`

### 4. Deployment Modes

**Mode 1: Full Deployment (Hackathon)**
```bash
# From root directory
docker build -t receipt-recon .
docker run -p 7860:7860 -e HF_TOKEN=your_token receipt-recon
```
Uses: Root `Dockerfile` → Runs the API server from `receipt-reconciliation/api/`

**Mode 2: Local Development**
```bash
# Terminal 1: Start API server
cd receipt-reconciliation
uvicorn api.main:app --port 7860

# Terminal 2: Run inference
python inference.py
```

## 🔍 File Locations Explained

### Root Level (Main Folder)
These files MUST be in root for OpenEnv compliance:
- `inference.py` - Required by OpenEnv validation
- `openenv.yaml` - Required by OpenEnv validation
- `Dockerfile` - Required for deployment
- `requirements.txt` - Required by Dockerfile

### Server Folder (`receipt-reconciliation/`)
This is your environment implementation:
- `environment/` - Core environment logic
- `api/` - HTTP API wrapper (the "server")

## 🎯 Why This Structure?

### OpenEnv Requirements
1. **inference.py in root** - Validation tooling looks for it there
2. **Dockerfile in root** - Standard Docker practice
3. **openenv.yaml in root** - Metadata discovery

### Best Practices
1. **Separation of concerns** - Environment logic separate from API
2. **Reusability** - Environment can be used without API
3. **Clarity** - Clear distinction between interface (API) and implementation (environment)

## 🚀 How to Deploy

### Step 1: Verify Structure
```powershell
# Check that Dockerfile is in root
Test-Path Dockerfile  # Should be True

# Check that inference.py is in root
Test-Path inference.py  # Should be True

# Verify no Dockerfile in server folder
Test-Path receipt-reconciliation/Dockerfile  # Should be False
```

### Step 2: Build Docker Image
```bash
# From root directory
docker build -t receipt-reconciliation .
```

### Step 3: Run Container
```bash
docker run -p 7860:7860 \
  -e HF_TOKEN=your_token \
  receipt-reconciliation
```

### Step 4: Test
```bash
# Health check
curl http://localhost:7860/health

# Reset endpoint
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_easy"}'
```

## ✅ Validation

Run validation to confirm structure is correct:
```powershell
.\validate-simple.ps1
```

Should show:
```
✓ Dockerfile in root
✓ inference.py in root
✓ openenv.yaml in root
✓ All checks passed
```

## 📝 Summary

**Correct Setup:**
- ✅ ONE Dockerfile in root (outermost folder)
- ✅ inference.py in root
- ✅ Server code in `receipt-reconciliation/api/`
- ✅ Environment code in `receipt-reconciliation/environment/`

**What Changed:**
- ❌ Removed duplicate `receipt-reconciliation/Dockerfile`
- ✅ Kept only root `Dockerfile`
- ✅ Root Dockerfile properly references the server path

Your project now follows OpenEnv best practices! 🎉
