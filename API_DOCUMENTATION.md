# API Documentation

Base URL: `http://localhost:8000/api/v1`

## Content Endpoints

### Submit URL for Processing
```http
POST /api/v1/content/url
Content-Type: application/json

{
  "url": "https://arxiv.org/abs/2301.12345"
}
```

**Response (201 Created):**
```json
{
  "message": "URL processed successfully",
  "content_id": 1,
  "status": "completed",
  "content": {
    "id": 1,
    "title": "Paper Title",
    "author": "John Doe",
    "source_type": "arxiv",
    "source_url": "https://arxiv.org/abs/2301.12345",
    "created_at": "2025-01-15T10:30:00Z",
    "summary": {
      "overview": "Detailed overview...",
      "key_insights": ["Insight 1", "Insight 2"],
      "implications": "Discussion..."
    },
    "themes": [
      {
        "theme_id": 1,
        "theme_name": "Machine Learning",
        "confidence": 0.92,
        "color": "#3B82F6"
      }
    ]
  }
}
```

### Upload PDF File
```http
POST /api/v1/content/upload
Content-Type: multipart/form-data

file: <binary PDF data>
```

**Response (201 Created):** Same structure as URL submission

### List Content
```http
GET /api/v1/content?page=1&page_size=10&source_type=arxiv&theme_id=1
```

**Query Parameters:**
- `page` (int, default=1): Page number
- `page_size` (int, default=10, max=100): Items per page
- `source_type` (string, optional): Filter by source type (twitter, pdf, arxiv, acm, web)
- `theme_id` (int, optional): Filter by theme ID

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Content Title",
      "author": "Author Name",
      "source_type": "arxiv",
      "source_url": "https://...",
      "created_at": "2025-01-15T10:30:00Z",
      "summary_preview": "First 200 chars of overview...",
      "themes": [...]
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

### Get Content Details
```http
GET /api/v1/content/{content_id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Content Title",
  "author": "Author Name",
  "source_type": "arxiv",
  "source_url": "https://...",
  "file_path": null,
  "publish_date": "2024-01-01T00:00:00Z",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "summary": {
    "overview": "Full overview text...",
    "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "implications": "Full implications text..."
  },
  "themes": [
    {
      "theme_id": 1,
      "theme_name": "Machine Learning",
      "confidence": 0.92,
      "color": "#3B82F6"
    }
  ],
  "extraction_metadata": {
    "arxiv_id": "2301.12345",
    "categories": ["cs.LG", "cs.AI"],
    ...
  }
}
```

### Delete Content
```http
DELETE /api/v1/content/{content_id}
```

**Response (204 No Content)**

---

## Search Endpoints

### Search Content
```http
GET /api/v1/search?q=machine+learning&theme_ids=1,2&source_types=arxiv,web&page=1&page_size=10
```

**Query Parameters:**
- `q` (string, optional): Search query (searches title, content, author)
- `theme_ids` (string, optional): Comma-separated theme IDs
- `source_types` (string, optional): Comma-separated source types
- `date_from` (datetime, optional): Filter by date from (ISO 8601)
- `date_to` (datetime, optional): Filter by date to (ISO 8601)
- `page` (int, default=1): Page number
- `page_size` (int, default=10, max=100): Items per page

**Response (200 OK):**
```json
{
  "query": "machine learning",
  "items": [...],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

---

## Theme Endpoints

### List All Themes
```http
GET /api/v1/themes
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Machine Learning",
    "description": "AI and ML related content",
    "color": "#3B82F6",
    "content_count": 15,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
]
```

### Get Theme Details
```http
GET /api/v1/themes/{theme_id}
```

**Response (200 OK):** Single theme object

### Get Content by Theme
```http
GET /api/v1/themes/{theme_id}/content?page=1&page_size=10
```

**Response (200 OK):** Same structure as List Content

### Create Theme
```http
POST /api/v1/themes
Content-Type: application/json

{
  "name": "Quantum Computing",
  "description": "Research on quantum computing",
  "color": "#8B5CF6"
}
```

**Response (201 Created):** Theme object

### Update Theme
```http
PUT /api/v1/themes/{theme_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description",
  "color": "#10B981"
}
```

**Response (200 OK):** Updated theme object

### Delete Theme
```http
DELETE /api/v1/themes/{theme_id}
```

**Response (204 No Content)**

---

## Health Check

### Check API Health
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "configured"
}
```

---

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

---

## Example Usage (cURL)

### Submit a URL
```bash
curl -X POST "http://localhost:8000/api/v1/content/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/abs/2301.12345"}'
```

### Search Content
```bash
curl "http://localhost:8000/api/v1/search?q=neural+networks&page=1&page_size=5"
```

### Upload PDF
```bash
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -F "file=@/path/to/paper.pdf"
```

---

## Rate Limits

The API implements rate limiting for external services:
- **Twitter API**: 100 requests per 15 minutes
- **Claude API**: 50 requests per minute
- **arXiv API**: 3 requests per second
- **General web scraping**: 10 requests per second

Internal API endpoints have no rate limits in the current implementation.
