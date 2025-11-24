from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import Note, NoteCreate, NoteUpdate, NotesList
from .repository import repo

app = FastAPI(
    title="Personal Notes Manager API",
    description=(
        "A simple FastAPI service that provides CRUD operations for personal notes. "
        "Notes are persisted to a local JSON file for simplicity. "
        "Use the endpoints below to create, list, retrieve, update, and delete notes."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Service health and diagnostics."},
        {"name": "notes", "description": "CRUD operations for personal notes."},
    ],
)

# CORS configuration for local development and general usage.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this appropriately.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Basic health check endpoint returning a simple JSON response."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
    summary="Create a new note",
    description="Create a new note by providing a title and content.",
    responses={
        201: {"description": "Note created", "model": Note},
        422: {"description": "Validation Error"},
    },
)
def create_note(payload: NoteCreate) -> Note:
    """Create a new note."""
    return repo.create_note(payload)


# PUBLIC_INTERFACE
@app.get(
    "/notes",
    response_model=NotesList,
    tags=["notes"],
    summary="List all notes",
    description="Retrieve a list of all notes stored in the system.",
)
def list_notes() -> NotesList:
    """List all notes currently stored."""
    items = repo.list_notes()
    return NotesList(items=items, total=len(items))


# PUBLIC_INTERFACE
@app.get(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Get a note by ID",
    description="Retrieve a single note by its unique identifier.",
    responses={
        200: {"description": "Note found", "model": Note},
        404: {"description": "Note not found"},
    },
)
def get_note(note_id: int) -> Note:
    """Retrieve a note by ID."""
    note = repo.get_note(note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@app.put(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Update a note by ID",
    description="Update an existing note's title and/or content by its ID.",
    responses={
        200: {"description": "Note updated", "model": Note},
        404: {"description": "Note not found"},
        422: {"description": "Validation Error"},
    },
)
def update_note(note_id: int, payload: NoteUpdate) -> Note:
    """Update a note's fields by ID."""
    note = repo.update_note(note_id, payload)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@app.delete(
    "/notes/{note_id}",
    tags=["notes"],
    summary="Delete a note by ID",
    description="Delete a note using its unique identifier.",
    responses={
        204: {"description": "Note deleted"},
        404: {"description": "Note not found"},
    },
)
def delete_note(note_id: int):
    """Delete a note by ID."""
    deleted = repo.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
