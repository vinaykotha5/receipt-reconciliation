"""
Receipt Reconciliation OpenEnv Server

This module provides the server entry point for the Receipt Reconciliation
OpenEnv environment. It starts a FastAPI server that exposes the environment
over HTTP for interaction with OpenEnv tools and agents.
"""

import os
import uvicorn
from receipt_reconciliation.api.main import app


def main():
    """Main entry point for the receipt-reconciliation-server command."""
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"Starting Receipt Reconciliation OpenEnv server on {host}:{port}")
    uvicorn.run(
        "receipt_reconciliation.api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()