#!/bin/bash

# Setup script for backend

echo "Setting up backend..."

# Navigate to backend directory
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your API keys!"
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your:"
echo "   - DATABASE_URL (PostgreSQL connection string)"
echo "   - ANTHROPIC_API_KEY"
echo "   - TWITTER_BEARER_TOKEN (optional)"
echo ""
echo "2. Ensure PostgreSQL is running and create the database"
echo "3. Install pgvector extension: psql -d your_database -c 'CREATE EXTENSION vector;'"
echo "4. Run migrations: cd backend && alembic upgrade head"
echo "5. Start the server: cd backend && uvicorn app.main:app --reload"
