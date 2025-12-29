#!/bin/bash

# Setup script for frontend

echo "Setting up frontend..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing npm dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the development server: cd frontend && npm run dev"
echo "2. Open http://localhost:5173 in your browser"
