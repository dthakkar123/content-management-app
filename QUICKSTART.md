# Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+ (optional, for async processing)
- Anthropic API key

## Step 1: Database Setup

```bash
# Create database
createdb content_db

# Install pgvector extension
psql content_db -c "CREATE EXTENSION vector;"
```

## Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your keys:
# DATABASE_URL=postgresql://user:password@localhost:5432/content_db
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://localhost:5432/content_db
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
TWITTER_BEARER_TOKEN=  # Optional
REDIS_URL=redis://localhost:6379
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

```bash
# Run database migrations
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Step 3: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# The .env file is already created with:
# VITE_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Step 4: Test the Application

1. Open http://localhost:5173 in your browser
2. Click "Add Content" button
3. Try adding:
   - An arXiv paper: `https://arxiv.org/abs/2301.07041`
   - A web article: Any blog post or article URL
   - A PDF: Upload any research paper

## Features You Can Use

### 1. Add Content
- **URL**: Twitter threads, arXiv papers, ACM library, web articles
- **PDF**: Upload research papers or documents

### 2. Search & Filter
- Search by keywords in title, content, or author
- Filter by themes (automatically generated)
- Combine search with theme filters

### 3. View Details
- Click any content card to see full summary
- Overview of the method/approach
- Key insights (bullet points)
- Implications and discussion

### 4. Automatic Categorization
- Themes emerge automatically after 10+ items
- AI categorizes content into relevant themes
- Confidence scores show match strength

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env
- Check ANTHROPIC_API_KEY is valid

### Frontend shows connection error
- Ensure backend is running on port 8000
- Check VITE_API_URL in frontend/.env
- Check CORS settings in backend/.env

### Migration errors
```bash
cd backend
alembic downgrade base  # Reset
alembic upgrade head    # Reapply
```

### Database connection issues
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql content_db -c "SELECT 1;"
```

## API Endpoints

See `API_DOCUMENTATION.md` for complete API reference.

Quick examples:

```bash
# Submit URL
curl -X POST "http://localhost:8000/api/v1/content/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/abs/2301.07041"}'

# Search
curl "http://localhost:8000/api/v1/search?q=machine+learning"

# List content
curl "http://localhost:8000/api/v1/content?page=1&page_size=10"
```

## Next Steps

1. Add your first content and explore the features
2. Try the search functionality
3. Check out the automatically generated themes
4. Upload a PDF and see the extraction quality

## Optional: Async Processing with Celery

For production use with large PDFs or high traffic:

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
cd backend
celery -A app.main.celery_app worker --loglevel=info

# Terminal 3: Start backend
uvicorn app.main:app --reload
```

Note: Async processing is configured but not required for the MVP.

## Support

- Backend API docs: http://localhost:8000/docs
- Frontend dev server: http://localhost:5173
- Issues: Report in GitHub repository
