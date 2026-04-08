# Receipt Reconciliation Investigator

**An OpenEnv environment for AI agent expense fraud detection and receipt reconciliation.**

## Project Structure

This project follows the OpenEnv hackathon requirements:

- `inference.py` - Baseline agent script (located at root per OpenEnv requirements)
- `receipt-reconciliation/` - Main environment implementation
  - `environment/` - Core environment package (env.py, models.py, tasks.py)
  - `api/` - FastAPI HTTP wrapper
  - `openenv.yaml` - Environment metadata
  - `Dockerfile` - Standalone deployment configuration
  - `README.md` - Full documentation

## Quick Start

### Run the baseline agent

```bash
export HF_TOKEN=your_token_here
export ENV_BASE_URL=http://localhost:7860
python inference.py
```

### Start the environment server

```bash
cd receipt-reconciliation
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 7860
```

### Docker deployment

```bash
docker build -t receipt-recon .
docker run -p 7860:7860 -e HF_TOKEN=your_token receipt-recon
```

## Full Documentation

For complete documentation, see [receipt-reconciliation/README.md](receipt-reconciliation/README.md).

## OpenEnv Compliance

This project structure ensures:
- `inference.py` is discoverable at the root directory (OpenEnv requirement)
- The environment package is properly organized in `receipt-reconciliation/environment/`
- Both standalone deployment (from `receipt-reconciliation/`) and root deployment work correctly
- All imports and Docker configurations are properly configured for both deployment modes
