# personal-notes-manager-45727-45736

Personal Notes Manager – FastAPI backend providing CRUD endpoints for notes with simple JSON-file persistence.

## Features
- FastAPI service with OpenAPI docs at `/docs`
- CRUD endpoints:
  - POST /notes
  - GET /notes
  - GET /notes/{id}
  - PUT /notes/{id}
  - DELETE /notes/{id}
- Simple JSON-file persistence stored under `notes_backend/src/data/notes.json`

## Getting Started

### Prerequisites
- Python 3.10+
- Pip

### Setup
1. Navigate to the backend directory:
   ```
   cd personal-notes-manager-45727-45736/notes_backend
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the server (development):
   ```
   uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
   ```

The API will be available at:
- OpenAPI JSON: http://localhost:3001/openapi.json
- Swagger UI: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc

## Data Storage
- Notes are stored in a JSON file at `notes_backend/src/data/notes.json`.
- The app writes after each change for simplicity.
- If the JSON is corrupted, the app will back it up to `notes_backend/src/data/notes.bak` and start fresh.

## Example Requests

Create a note:
```
POST /notes
Content-Type: application/json

{
  "title": "My first note",
  "content": "Hello notes!"
}
```

List notes:
```
GET /notes
```

Get by id:
```
GET /notes/1
```

Update:
```
PUT /notes/1
Content-Type: application/json

{
  "title": "Updated title"
}
```

Delete:
```
DELETE /notes/1
```

## Notes
- No external database or services required.
- CORS is open for development; restrict `allow_origins` in production if needed.
