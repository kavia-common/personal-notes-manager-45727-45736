from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class NoteCreate(BaseModel):
    """Model for creating a new note."""
    title: str = Field(..., description="Title of the note", min_length=1, max_length=200)
    content: str = Field(..., description="Content/body of the note", min_length=1)


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Model for updating an existing note. All fields are optional."""
    title: Optional[str] = Field(None, description="Updated title of the note", min_length=1, max_length=200)
    content: Optional[str] = Field(None, description="Updated content/body of the note", min_length=1)


# PUBLIC_INTERFACE
class Note(BaseModel):
    """Model representing a stored note."""
    id: int = Field(..., description="Unique identifier for the note")
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content/body of the note")
    created_at: datetime = Field(..., description="Timestamp when the note was created (UTC)")
    updated_at: datetime = Field(..., description="Timestamp when the note was last updated (UTC)")


# PUBLIC_INTERFACE
class NotesList(BaseModel):
    """Model wrapping a list of notes for response usage."""
    items: List[Note] = Field(..., description="List of notes returned by the API")
    total: int = Field(..., description="Total count of notes in the list")
