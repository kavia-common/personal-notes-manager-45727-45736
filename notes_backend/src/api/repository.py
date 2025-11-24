import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .models import Note, NoteCreate, NoteUpdate


class NotesRepository:
    """Simple JSON-file backed repository with in-memory cache and thread-safety.

    This repository:
    - Loads notes from a JSON file on first use (if present)
    - Persists on every write to keep it simple and durable
    - Uses a re-entrant lock to avoid concurrency issues within a single process
    - Generates incremental integer IDs
    """

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self._lock = threading.RLock()
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self._storage_path: Path = storage_path or (data_dir / "notes.json")
        self._notes: Dict[int, Note] = {}
        self._next_id: int = 1
        self._load()

    def _load(self) -> None:
        with self._lock:
            if not self._storage_path.exists():
                # Initialize empty storage
                self._persist()
                return
            try:
                raw = json.loads(self._storage_path.read_text(encoding="utf-8"))
                items = raw.get("items", [])
                self._notes.clear()
                for item in items:
                    # Parse datetimes back
                    item["created_at"] = datetime.fromisoformat(item["created_at"])
                    item["updated_at"] = datetime.fromisoformat(item["updated_at"])
                    note = Note(**item)
                    self._notes[note.id] = note
                # Determine next id
                self._next_id = max(self._notes.keys(), default=0) + 1
            except Exception:
                # If the file is corrupted, start fresh but keep the bad file as .bak
                backup = self._storage_path.with_suffix(".bak")
                try:
                    self._storage_path.rename(backup)
                except Exception:
                    pass
                self._notes.clear()
                self._next_id = 1
                self._persist()

    def _persist(self) -> None:
        with self._lock:
            serializable = {
                "items": [
                    {
                        "id": n.id,
                        "title": n.title,
                        "content": n.content,
                        "created_at": n.created_at.isoformat(),
                        "updated_at": n.updated_at.isoformat(),
                    }
                    for n in self._notes.values()
                ]
            }
            tmp_path = self._storage_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
            tmp_path.replace(self._storage_path)

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Note]:
        """Return all notes."""
        with self._lock:
            return list(sorted(self._notes.values(), key=lambda n: n.id))

    # PUBLIC_INTERFACE
    def create_note(self, payload: NoteCreate) -> Note:
        """Create a new note from the given payload."""
        with self._lock:
            now = datetime.now(timezone.utc)
            note = Note(
                id=self._next_id,
                title=payload.title,
                content=payload.content,
                created_at=now,
                updated_at=now,
            )
            self._notes[note.id] = note
            self._next_id += 1
            self._persist()
            return note

    # PUBLIC_INTERFACE
    def get_note(self, note_id: int) -> Optional[Note]:
        """Fetch a note by ID."""
        with self._lock:
            return self._notes.get(note_id)

    # PUBLIC_INTERFACE
    def update_note(self, note_id: int, payload: NoteUpdate) -> Optional[Note]:
        """Update fields of a note; returns None if not found."""
        with self._lock:
            note = self._notes.get(note_id)
            if note is None:
                return None
            updated = note.model_copy()
            has_change = False
            if payload.title is not None and payload.title != note.title:
                updated.title = payload.title
                has_change = True
            if payload.content is not None and payload.content != note.content:
                updated.content = payload.content
                has_change = True
            if has_change:
                updated.updated_at = datetime.now(timezone.utc)
                self._notes[note_id] = updated
                self._persist()
                return updated
            return note

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID. Returns True if a note was deleted."""
        with self._lock:
            removed = self._notes.pop(note_id, None)
            if removed is not None:
                self._persist()
                return True
            return False


# A module-level singleton repository instance for simple usage in routes.
repo = NotesRepository()
