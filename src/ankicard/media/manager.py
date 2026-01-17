import uuid


def generate_unique_id() -> str:
    """Generate unique 8-character ID."""
    return str(uuid.uuid4())[:8]


def generate_media_filenames(unique_id: str) -> dict[str, str]:
    """Generate media filenames."""
    return {
        "audio": f"anki_{unique_id}.mp3",
        "image": f"anki_{unique_id}.jpg",
    }
