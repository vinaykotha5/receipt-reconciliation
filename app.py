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
    # Run uvicorn from inside receipt-reconciliation/ so api.main can import environment.*
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "api.main:app",
         "--host", "0.0.0.0", "--port", port],
        cwd=os.path.join(os.path.dirname(__file__), "receipt-reconciliation"),
        check=True
    )