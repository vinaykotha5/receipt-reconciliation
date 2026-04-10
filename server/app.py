"""
server/app.py — OpenEnv multi-mode deployment entry point.

Required by: openenv validate (multi-mode deployment check).
Starts the Receipt Reconciliation FastAPI environment server.
"""

import os
import sys

# Add receipt-reconciliation to path so api.main can be imported
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "receipt-reconciliation")
)

import uvicorn
from api.main import app  # noqa: E402  (import after sys.path setup)


def main() -> None:
    """Entry point for the receipt-reconciliation-server command."""
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting Receipt Reconciliation server on {host}:{port}", flush=True)
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
