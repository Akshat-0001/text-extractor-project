# Async Document Processing System

A full-stack application for uploading documents, processing them asynchronously, tracking progress in real-time, and exporting results.

## Architecture Overview

### Stack
- **Frontend**: React + TypeScript + Vite
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Background Jobs**: Celery
- **Message Broker**: Redis (for Celery + Pub/Sub)
- **Progress Tracking**: Server-Sent Events (SSE)

### System Flow

1. User uploads document(s) via React frontend
2. FastAPI saves files and creates job records in PostgreSQL
3. Celery worker picks up job and processes it through 6 stages
4. Worker publishes progress events to Redis Pub/Sub
5. Frontend subscribes to SSE endpoint that streams Redis events
6. Upon completion, extracted data is stored in database
7. User can review, edit, finalize, and export results

### Project Structure

```
/backend
  main.py           ← All FastAPI routes
  models.py         ← SQLAlchemy models
  schemas.py        ← Pydantic schemas
  database.py       ← DB session setup
  worker.py         ← Celery app + processing task
  services.py       ← Business logic
  requirements.txt
  Dockerfile

/frontend
  /src
    /pages
      Dashboard.tsx  ← Job list with search/filter/sort
      Upload.tsx     ← Upload form
      Detail.tsx     ← Review, edit, finalize, export
    /components
      JobCard.tsx
      ProgressBar.tsx
    api.ts           ← All API calls
    main.tsx
    index.css
  package.json
  Dockerfile

docker-compose.yml   ← Full stack orchestration
```

## Setup Instructions

### Option 1: Docker Compose (Recommended)

1. **Prerequisites**
   - Docker and Docker Compose installed

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Prerequisites**
   - Python 3.11+
   - PostgreSQL running on localhost:5432
   - Redis running on localhost:6379

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

4. **Run FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Run Celery worker** (in separate terminal)
   ```bash
   celery -A worker worker --loglevel=info
   ```

#### Frontend Setup

1. **Prerequisites**
   - Node.js 18+

2. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

## Features

### Implemented

✅ Upload single or multiple documents  
✅ Async processing with Celery (6 stages)  
✅ Real-time progress tracking via SSE  
✅ Job states: queued, processing, completed, failed  
✅ Dashboard with search, filter by status, sort by date  
✅ Detail page with extracted data review  
✅ Edit extracted fields (title, category, summary, keywords)  
✅ Finalize reviewed results  
✅ Retry failed jobs  
✅ Export as JSON or CSV  
✅ Docker Compose setup  

### Processing Stages

1. **document_received** - Job created
2. **parsing_started** - Begin parsing
3. **parsing_completed** - Parsing done
4. **extraction_started** - Begin field extraction
5. **extraction_completed** - Extraction done
6. **storing_result** - Save to database
7. **job_completed** - Processing complete

### Extracted Fields

The worker extracts these fields from each document:
- **Title**: Derived from filename
- **Category**: Set to "Document"
- **Summary**: Simple description
- **Keywords**: Words from filename (>3 chars)

*Note: Processing logic is simplified for demonstration. Real implementation would use NLP/OCR libraries.*

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload documents |
| GET | `/jobs` | List all jobs (with search/filter/sort) |
| GET | `/jobs/{id}` | Get job details |
| GET | `/jobs/{id}/progress` | SSE stream for progress |
| POST | `/jobs/{id}/retry` | Retry failed job |
| PUT | `/jobs/{id}/result` | Update extracted fields |
| POST | `/jobs/{id}/finalize` | Mark job as finalized |
| GET | `/jobs/{id}/export?format=json\|csv` | Export job data |

## Assumptions

1. **File Storage**: Files saved to local `uploads/` directory (not cloud storage)
2. **Authentication**: Not implemented (would add JWT in production)
3. **Processing Logic**: Simplified extraction (real app would use NLP/OCR)
4. **Error Handling**: Basic error handling at task level
5. **Scalability**: Single worker setup (would use multiple workers in production)
6. **File Types**: Accepts any file type (real app would validate)

## Tradeoffs

### Simplicity vs Features
- Kept all routes in `main.py` instead of splitting into routers
- Used plain SQLAlchemy (not async) for simplicity
- No file type validation or size limits
- Basic error messages without detailed logging

### Performance vs Complexity
- Single Celery worker (easy to scale horizontally)
- No caching layer (could add Redis caching)
- Synchronous DB operations (async would improve throughput)

### Security vs Speed
- No authentication (would add in production)
- CORS allows all origins (would restrict in production)
- No rate limiting (would add in production)

## Limitations

1. **No Authentication**: Anyone can upload/view/edit jobs
2. **No File Validation**: Accepts any file type/size
3. **Simple Processing**: Extraction logic is basic
4. **No Cancellation**: Cannot cancel running jobs
5. **No Pagination**: All jobs loaded at once
6. **Local Storage**: Files stored locally, not in cloud
7. **No Tests**: Would add unit/integration tests in production

## Testing

### Sample Test File

A `sample_test.txt` file is included for testing uploads.

### Manual Testing Steps

1. Navigate to http://localhost:5173
2. Click "Upload Documents"
3. Select `sample_test.txt` (or any file)
4. Click "Upload"
5. Watch job appear in dashboard with "queued" status
6. Click on job to view details
7. Watch progress bar update in real-time
8. Once completed, review extracted data
9. Click "Edit" to modify fields
10. Click "Finalize" to lock the record
11. Export as JSON or CSV

## Development Notes

### AI Tools Used
This project was built with assistance from AI tools for:
- Boilerplate code generation
- Project structure setup
- Documentation writing

### Code Style
- No excessive comments or step-by-step narration
- Flat code structure, minimal nesting
- Error handling at top level only
- No unnecessary abstractions or wrapper functions
- Plain fetch API (no axios/react-query)
- Plain useState (no Redux/Zustand)

## Future Enhancements

- [ ] Add authentication (JWT)
- [ ] Implement job cancellation
- [ ] Add pagination for job list
- [ ] Support cloud storage (S3/GCS)
- [ ] Add file type validation
- [ ] Implement rate limiting
- [ ] Add comprehensive tests
- [ ] Add logging and monitoring
- [ ] Support batch operations
- [ ] Add webhook notifications
