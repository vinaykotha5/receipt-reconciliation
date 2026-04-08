"""
OpenEnv Server Entry Point

This file provides the server entry point expected by OpenEnv validation.
It delegates to the actual application in the receipt_reconciliation package.
"""

from receipt_reconciliation.app import main as app_main


def main():
    """Main entry point for the receipt-reconciliation-server command."""
    app_main()


if __name__ == "__main__":
    main()