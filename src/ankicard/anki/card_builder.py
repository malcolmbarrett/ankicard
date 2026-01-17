import genanki
from .models import IMMERSION_KIT_MODEL


def create_note(
    expression: str,
    english: str,
    reading: str,
    image_filename: str | None,
    audio_filename: str,
    unique_id: str,
) -> genanki.Note:
    """Create an Anki note."""
    image_field = f'<img src="{image_filename}">' if image_filename else ""
    return genanki.Note(
        model=IMMERSION_KIT_MODEL,
        fields=[
            expression,
            english,
            reading,
            image_field,
            f"[sound:{audio_filename}]",
            unique_id,
        ],
    )


def create_deck(
    deck_name: str = "Immersion Kit", deck_id: int = 2059400110
) -> genanki.Deck:
    """Create an Anki deck."""
    return genanki.Deck(deck_id, deck_name)


def export_package(
    deck: genanki.Deck, media_files: list[str], output_path: str
) -> None:
    """Export Anki package to .apkg file."""
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(output_path)
