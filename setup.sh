#!/bin/bash
# OpenEnv Receipt Reconciliation - Setup Script (Bash)
# This script sets up the virtual environment and installs all dependencies

echo "========================================"
echo "OpenEnv Receipt Reconciliation Setup"
echo "========================================"
echo ""

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "✗ Python not found. Please install Python 3.11+"
        exit 1
    else
        PYTHON_CMD=python3
    fi
else
    PYTHON_CMD=python
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "✓ Found: $PYTHON_VERSION"

# Check if venv already exists
if [ -d "venv" ]; then
    echo ""
    echo "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Removing existing venv..."
        rm -rf venv
    else
        echo "Using existing venv..."
        echo ""
        echo "To activate the virtual environment, run:"
        echo "  source venv/bin/activate"
        exit 0
    fi
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

if [ $? -ne 0 ]; then
    echo "✗ Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

# Optional: Install openenv-core
echo ""
read -p "Install openenv-core CLI tools? (Y/n): " response
if [[ ! "$response" =~ ^[Nn]$ ]]; then
    echo "Installing openenv-core..."
    pip install openenv-core --quiet
    if [ $? -eq 0 ]; then
        echo "✓ openenv-core installed"
    else
        echo "✗ Failed to install openenv-core (optional)"
    fi
fi

# Test imports
echo ""
echo "Testing imports..."
python -c "import sys; sys.path.insert(0, 'receipt-reconciliation'); from environment.env import ReceiptReconciliationEnv; print('✓ Imports work!')"

if [ $? -eq 0 ]; then
    echo "✓ Environment setup complete!"
else
    echo "✗ Import test failed"
fi

# Summary
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Set your Hugging Face token:"
echo "   export HF_TOKEN='your_token_here'"
echo ""
echo "2. Run the inference script:"
echo "   python inference.py"
echo ""
echo "3. Or start the API server:"
echo "   cd receipt-reconciliation"
echo "   uvicorn api.main:app --host 0.0.0.0 --port 7860"
echo ""
echo "To activate the virtual environment later:"
echo "  source venv/bin/activate"
echo ""
