"""Read and parse existing .apkg files."""

import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass, field


FIELD_SEPARATOR = "\x1f"


@dataclass
class AnkiNote:
    """A note extracted from an .apkg file."""

    fields: list[str]
    guid: str
    model_id: int
    tags: str = ""

    @property
    def expression(self) -> str:
        return self.fields[0] if len(self.fields) > 0 else ""

    @property
    def english(self) -> str:
        return self.fields[1] if len(self.fields) > 1 else ""

    @property
    def reading(self) -> str:
        return self.fields[2] if len(self.fields) > 2 else ""

    @property
    def screenshot(self) -> str:
        return self.fields[3] if len(self.fields) > 3 else ""

    @property
    def audio_sentence(self) -> str:
        return self.fields[4] if len(self.fields) > 4 else ""

    @property
    def note_id(self) -> str:
        return self.fields[5] if len(self.fields) > 5 else ""


@dataclass
class ApkgContents:
    """Contents extracted from an .apkg file."""

    notes: list[AnkiNote]
    media_mapping: dict[str, str] = field(default_factory=dict)
    deck_name: str = ""


def read_apkg(apkg_path: str) -> ApkgContents:
    """Read an .apkg file and extract notes and media mapping.

    Args:
        apkg_path: Path to the .apkg file.

    Returns:
        ApkgContents with notes, media mapping, and deck name.
    """
    with zipfile.ZipFile(apkg_path) as z:
        media_mapping = json.loads(z.read("media"))

        db_name = _find_db_name(z)
        with tempfile.TemporaryDirectory() as td:
            z.extract(db_name, td)
            db_path = os.path.join(td, db_name)
            conn = sqlite3.connect(db_path)
            try:
                notes = _read_notes(conn)
                deck_name = _read_deck_name(conn)
            finally:
                conn.close()

    return ApkgContents(
        notes=notes,
        media_mapping=media_mapping,
        deck_name=deck_name,
    )


def extract_media(apkg_path: str, output_dir: str) -> list[str]:
    """Extract media files from an .apkg file.

    Args:
        apkg_path: Path to the .apkg file.
        output_dir: Directory to extract media files into.

    Returns:
        List of extracted media file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    extracted = []

    with zipfile.ZipFile(apkg_path) as z:
        media_mapping = json.loads(z.read("media"))
        for archive_name, real_name in media_mapping.items():
            if archive_name in z.namelist():
                dest = os.path.join(output_dir, real_name)
                with z.open(archive_name) as src, open(dest, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted.append(dest)

    return extracted


def _find_db_name(z: zipfile.ZipFile) -> str:
    """Find the SQLite database file in the archive."""
    for name in ("collection.anki21", "collection.anki2"):
        if name in z.namelist():
            return name
    raise ValueError("No collection database found in .apkg file")


def _read_notes(conn: sqlite3.Connection) -> list[AnkiNote]:
    """Read all notes from the database."""
    rows = conn.execute("SELECT guid, mid, tags, flds FROM notes").fetchall()
    return [
        AnkiNote(
            guid=row[0],
            model_id=row[1],
            tags=row[2],
            fields=row[3].split(FIELD_SEPARATOR),
        )
        for row in rows
    ]


def _read_deck_name(conn: sqlite3.Connection) -> str:
    """Read the primary deck name from the database."""
    row = conn.execute("SELECT decks FROM col").fetchone()
    if not row:
        return ""
    decks = json.loads(row[0])
    # Return the first non-default deck name, or "Default"
    for deck in decks.values():
        if deck["name"] != "Default":
            return deck["name"]
    return "Default"
