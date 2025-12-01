#!/bin/bash
# Setup script for Career Planning Education Agent
# This script handles all installation and configuration

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      Career Planning Education Agent - Setup Script            ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Check Python version
echo ""
echo "Checking Python installation..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✓ Python $python_version detected"

if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check pip
echo ""
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "✗ pip3 is not installed. Please install pip3."
    exit 1
fi
echo "✓ pip3 is available"

# Create virtual environment (optional but recommended)
echo ""
echo "Setting up virtual environment (recommended)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed successfully"

# Setup environment file
echo ""
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
    echo "  Please edit .env and add your GEMINI_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Verify API key
echo ""
echo "Checking API configuration..."
if grep -q "your-api-key-here" .env; then
    echo "⚠ WARNING: API key not configured!"
    echo "  Please edit .env and add your GEMINI_API_KEY"
    echo "  Get it from: https://aistudio.google.com/app/apikey"
else
    echo "✓ API key appears to be configured"
fi

# Test imports
echo ""
echo "Testing Python imports..."
python3 -c "import google.generativeai as genai; print('✓ google.generativeai imported successfully')" || {
    echo "✗ Failed to import google.generativeai"
    exit 1
}

python3 -c "import dotenv; print('✓ python-dotenv imported successfully')" || {
    echo "✗ Failed to import dotenv"
    exit 1
}

# Create necessary directories
echo ""
echo "Creating output directories..."
mkdir -p outputs
mkdir -p logs
echo "✓ Directories created"

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    SETUP COMPLETE! 🎉                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Run: python main.py"
echo "3. Or run examples: python examples.py"
echo "4. Or run advanced examples: python integration_example.py"
echo ""
echo "To deactivate virtual environment: deactivate"
echo "To reactivate: source venv/bin/activate"
echo ""
