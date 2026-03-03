import os

from ankicard.anki.reader import (
    AnkiNote,
    read_apkg,
    extract_media,
)
from ankicard.anki.card_builder import create_note, create_deck, export_package


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "test_apkg")


class TestAnkiNote:
    """Tests for AnkiNote dataclass."""

    def test_properties_with_full_fields(self):
        note = AnkiNote(
            fields=["expr", "eng", "read", "img", "audio", "id123"],
            guid="abc",
            model_id=1,
        )
        assert note.expression == "expr"
        assert note.english == "eng"
        assert note.reading == "read"
        assert note.screenshot == "img"
        assert note.audio_sentence == "audio"
        assert note.note_id == "id123"

    def test_properties_with_empty_fields(self):
        note = AnkiNote(fields=[], guid="abc", model_id=1)
        assert note.expression == ""
        assert note.english == ""
        assert note.note_id == ""


class TestReadApkg:
    """Tests for reading .apkg files."""

    def test_read_durarara_fixture(self):
        path = os.path.join(FIXTURES_DIR, "anime_durarara___000000097.apkg")
        contents = read_apkg(path)

        assert len(contents.notes) == 1
        assert contents.deck_name == "Immersion Kit"

        note = contents.notes[0]
        assert note.expression == "ああ　ラジオとか雑誌投稿とか？"
        assert "radio" in note.english.lower() or "magazine" in note.english.lower()
        assert note.model_id == 1239585222
        assert len(note.fields) == 6

    def test_read_psycho_pass_fixture(self):
        path = os.path.join(FIXTURES_DIR, "anime_psycho_pass_000001483.apkg")
        contents = read_apkg(path)

        assert len(contents.notes) == 1
        assert contents.deck_name == "Immersion Kit"

    def test_media_mapping(self):
        path = os.path.join(FIXTURES_DIR, "anime_durarara___000000097.apkg")
        contents = read_apkg(path)

        assert len(contents.media_mapping) == 2
        filenames = list(contents.media_mapping.values())
        assert any(f.endswith(".jpg") for f in filenames)
        assert any(f.endswith(".mp3") for f in filenames)

    def test_round_trip(self, tmp_path):
        """Create an .apkg with genanki, read it back with reader."""
        deck = create_deck("Test Deck", 9999)
        note = create_note(
            expression="テスト",
            english="Test",
            reading="テスト",
            image_filename=None,
            audio_filename="test.mp3",
            unique_id="rt001",
        )
        deck.add_note(note)

        apkg_path = str(tmp_path / "round_trip.apkg")
        export_package(deck, [], apkg_path)

        contents = read_apkg(apkg_path)
        assert len(contents.notes) == 1
        assert contents.notes[0].expression == "テスト"
        assert contents.notes[0].english == "Test"
        assert contents.notes[0].note_id == "rt001"
        assert len(contents.notes[0].fields) == 39


class TestExtractMedia:
    """Tests for media extraction."""

    def test_extract_media_from_fixture(self, tmp_path):
        path = os.path.join(FIXTURES_DIR, "anime_durarara___000000097.apkg")
        extracted = extract_media(path, str(tmp_path))

        assert len(extracted) == 2
        for f in extracted:
            assert os.path.exists(f)
            assert os.path.getsize(f) > 0

    def test_extract_creates_output_dir(self, tmp_path):
        output_dir = str(tmp_path / "new_subdir")
        path = os.path.join(FIXTURES_DIR, "anime_durarara___000000097.apkg")
        extract_media(path, output_dir)

        assert os.path.isdir(output_dir)
