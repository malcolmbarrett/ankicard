import genanki
from .models import (
    IMMERSION_KIT_MODEL,
    DECK_ID_SENTENCES,
    DECK_ID_VOCAB,
    DECK_ID_KANJI,
    DECK_ID_GRAMMAR,
)


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
    core_fields = [
        expression,
        english,
        reading,
        image_field,
        f"[sound:{audio_filename}]",
        unique_id,
    ]
    # Pad with empty strings for the 33 additional fields (vocab, kanji, grammar)
    fields = core_fields + [""] * (len(IMMERSION_KIT_MODEL.fields) - len(core_fields))
    return genanki.Note(
        model=IMMERSION_KIT_MODEL,
        fields=fields,
    )


def create_note_from_fields(fields: list[str]) -> genanki.Note:
    """Create an Anki note from raw field values, padding to the model's field count."""
    total = len(IMMERSION_KIT_MODEL.fields)
    padded = (fields + [""] * total)[:total]
    return genanki.Note(
        model=IMMERSION_KIT_MODEL,
        fields=padded,
    )


def create_deck(
    deck_name: str = "Immersion Kit::Sentences", deck_id: int = DECK_ID_SENTENCES
) -> genanki.Deck:
    """Create an Anki deck."""
    return genanki.Deck(deck_id, deck_name)


def create_all_decks() -> list[genanki.Deck]:
    """Create all subdecks for the Immersion Kit deck structure."""
    return [
        genanki.Deck(DECK_ID_SENTENCES, "Immersion Kit::Sentences"),
        genanki.Deck(DECK_ID_VOCAB, "Immersion Kit::Components::Vocab"),
        genanki.Deck(DECK_ID_KANJI, "Immersion Kit::Components::Kanji"),
        genanki.Deck(DECK_ID_GRAMMAR, "Immersion Kit::Components::Grammar"),
    ]


def export_package(
    deck_or_decks: genanki.Deck | list[genanki.Deck],
    media_files: list[str],
    output_path: str,
) -> None:
    """Export Anki package to .apkg file."""
    package = genanki.Package(deck_or_decks)
    package.media_files = media_files
    package.write_to_file(output_path)
