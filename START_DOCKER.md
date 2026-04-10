# How to Start Docker

## Docker Daemon Not Running

The error message indicates Docker Desktop is not running:
```
ERROR: error during connect: this error may indicate that the docker daemon is not running
```

## Steps to Start Docker

### Windows:

1. **Open Docker Desktop**
   - Press `Windows key`
   - Type "Docker Desktop"
   - Click on Docker Desktop application

2. **Wait for Docker to Start**
   - You'll see the Docker icon in the system tray (bottom right)
   - Wait until the icon stops animating
   - Icon should show "Docker Desktop is running"

3. **Verify Docker is Running**
   ```powershell
   docker info
   ```
   Should show server information without errors

### Alternative: Start from Command Line

```powershell
# Start Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait a minute for it to start
Start-Sleep -Seconds 60

# Verify
docker info
```

## After Docker Starts

Run the manual test:
```powershell
.\manual-test.ps1
```

This will:
1. ✅ Check Docker installation
2. ✅ Check Docker daemon
3. ✅ Build Docker image
4. ✅ Run container
5. ✅ Test all API endpoints
6. ✅ Verify everything works

## If You Don't Want to Use Docker

You can still test without Docker:

### Option 1: Run API Server Directly
```powershell
# Terminal 1: Start API server
cd receipt-reconciliation
python -m uvicorn api.main:app --host 0.0.0.0 --port 7860

# Terminal 2: Test endpoints
curl http://localhost:7860/health
curl http://localhost:7860/tasks
```

### Option 2: Just Validate
```powershell
# Run validation (no Docker needed)
.\validate-simple.ps1
```

Your project will still work on Hugging Face Spaces even if you can't test Docker locally!
