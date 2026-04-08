"""
HF Spaces entrypoint — delegates to the FastAPI app.
Hugging Face Spaces with SDK=docker uses the Dockerfile directly,
but this file supports the 'gradio' SDK fallback route.
"""
import os
import subprocess
import sys


def main():
    """Main entry point for the receipt-reconciliation-server command."""
    port = os.environ.get("PORT", "7860")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "api.main:app",
         "--host", "0.0.0.0", "--port", port],
        check=True
    )


if __name__ == "__main__":
    main()
