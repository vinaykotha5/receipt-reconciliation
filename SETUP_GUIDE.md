# Setup Guide - Receipt Reconciliation OpenEnv

This guide will help you set up the development environment for the Receipt Reconciliation OpenEnv project.

## Quick Setup

### Windows (PowerShell)

```powershell
# Run the setup script
.\setup.ps1

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

### Linux/Mac/Git Bash

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# Activate the virtual environment
source venv/bin/activate
```

## Manual Setup

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac/Git Bash)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Optional: Install OpenEnv CLI tools
pip install openenv-core
```

### 3. Verify Installation

```bash
# Test imports
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.env import ReceiptReconciliationEnv; print('✓ Setup successful!')"
```

## Environment Variables

Before running the inference script, set these environment variables:

### Windows (PowerShell)

```powershell
$env:HF_TOKEN = "your_huggingface_token_here"
$env:API_BASE_URL = "https://router.huggingface.co/v1"  # Optional, has default
$env:MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"  # Optional, has default
$env:ENV_BASE_URL = "http://localhost:7860"  # Optional, has default
```

### Linux/Mac/Git Bash

```bash
export HF_TOKEN="your_huggingface_token_here"
export API_BASE_URL="https://router.huggingface.co/v1"  # Optional, has default
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"  # Optional, has default
export ENV_BASE_URL="http://localhost:7860"  # Optional, has default
```

## Running the Project

### Option 1: Run Inference Script

```bash
# Make sure venv is activated and HF_TOKEN is set
python inference.py
```

### Option 2: Start API Server + Run Inference

Terminal 1 (API Server):
```bash
cd receipt-reconciliation
uvicorn api.main:app --host 0.0.0.0 --port 7860
```

Terminal 2 (Inference):
```bash
# Set ENV_BASE_URL to point to the API server
export ENV_BASE_URL="http://localhost:7860"  # or use $env: for PowerShell
python inference.py
```

### Option 3: Docker

```bash
# Build the Docker image
docker build -t receipt-recon .

# Run the container
docker run -p 7860:7860 -e HF_TOKEN=your_token receipt-recon
```

## Testing

Run the test suites to verify everything works:

```bash
# Bug condition tests (should all pass after fix)
python test_bug_condition.py

# Preservation tests (verify no regressions)
python test_preservation.py
```

## Deployment to Hugging Face

### Using OpenEnv CLI

```bash
# Make sure openenv-core is installed
pip install openenv-core

# Push to Hugging Face Spaces
openenv push
```

### Manual Deployment

1. Create a new Space on Hugging Face Hub
2. Set SDK to "Docker"
3. Push your code to the Space repository
4. Add your HF_TOKEN as a Space secret
5. The Dockerfile will handle the rest

## Troubleshooting

### Import Errors

If you get import errors when running inference.py:

```bash
# Make sure you're in the project root directory
pwd  # or cd on Windows

# Verify the path setup in inference.py
python -c "import sys; print(sys.path)"
```

### Docker Build Fails

```bash
# Make sure Docker daemon is running
docker info

# Check if requirements.txt exists in root
ls requirements.txt  # or dir on Windows
```

### API Server Won't Start

```bash
# Check if port 7860 is already in use
netstat -ano | findstr :7860  # Windows
lsof -i :7860  # Linux/Mac

# Try a different port
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
root/
├── inference.py              # Baseline agent (must be at root)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── openenv.yaml              # OpenEnv metadata
├── README.md                 # Project documentation
├── setup.ps1                 # Windows setup script
├── setup.sh                  # Linux/Mac setup script
├── SETUP_GUIDE.md            # This file
├── test_bug_condition.py     # Bug condition tests
├── test_preservation.py      # Preservation tests
└── receipt-reconciliation/   # Main implementation
    ├── environment/          # Core environment package
    │   ├── __init__.py
    │   ├── env.py           # Environment logic
    │   ├── models.py        # Pydantic models
    │   └── tasks.py         # Task definitions
    ├── api/                 # FastAPI wrapper
    │   ├── __init__.py
    │   └── main.py          # API endpoints
    ├── app.py               # HF Spaces entrypoint
    ├── Dockerfile           # Standalone deployment
    ├── openenv.yaml         # Environment metadata
    ├── README.md            # Full documentation
    └── requirements.txt     # Dependencies
```

## Getting Help

- Check the main README: [receipt-reconciliation/README.md](receipt-reconciliation/README.md)
- Review the bugfix summary: [BUGFIX_SUMMARY.md](BUGFIX_SUMMARY.md)
- OpenEnv documentation: https://github.com/meta-pytorch/OpenEnv
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces

## Next Steps

1. ✅ Set up virtual environment (you're here!)
2. ⬜ Test inference script locally
3. ⬜ Deploy to Hugging Face Spaces
4. ⬜ Submit to OpenEnv hackathon
