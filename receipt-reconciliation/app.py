"""
HF Spaces entrypoint — delegates to the FastAPI app.
Hugging Face Spaces with SDK=docker uses the Dockerfile directly,
but this file supports the 'gradio' SDK fallback route.
"""
import os
import subprocess
import sys

if __name__ == "__main__":
    port = os.environ.get("PORT", "7860")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "receipt-reconciliation.api.main:app",
         "--host", "0.0.0.0", "--port", port],
        check=True
    )
