import pytest
from ankicard.core.furigana import to_hiragana, get_furigana, get_tokenizer


class TestToHiragana:
    """Tests for katakana to hiragana conversion."""

    def test_katakana_to_hiragana(self, sample_katakana, sample_hiragana):
        """Test basic katakana to hiragana conversion."""
        result = to_hiragana(sample_katakana)
        assert result == sample_hiragana

    def test_mixed_text_preserves_non_katakana(self):
        """Test that non-katakana characters are preserved."""
        text = "ABCカタカナ123"
        result = to_hiragana(text)
        assert result == "ABCかたかな123"

    def test_empty_string(self):
        """Test empty string handling."""
        assert to_hiragana("") == ""

    def test_hiragana_unchanged(self):
        """Test that hiragana is not affected."""
        hiragana = "ひらがな"
        assert to_hiragana(hiragana) == hiragana

    def test_full_katakana_range(self):
        """Test conversion across full katakana range."""
        # Test a few key characters
        assert to_hiragana("ア") == "あ"
        assert to_hiragana("ン") == "ん"
        assert to_hiragana("ガ") == "が"


class TestGetFurigana:
    """Tests for furigana generation."""

    def test_simple_kanji(self):
        """Test furigana generation for simple kanji."""
        result = get_furigana("日本語")
        assert "日本語[にほんご]" in result

    def test_mixed_kanji_hiragana(self, sample_japanese_with_kanji):
        """Test furigana with mixed kanji and hiragana."""
        result = get_furigana(sample_japanese_with_kanji)
        # Should contain furigana for kanji but not hiragana
        assert "[" in result
        assert "]" in result

    def test_only_hiragana(self):
        """Test that pure hiragana text has no furigana."""
        result = get_furigana("ひらがな")
        assert "[" not in result
        assert "]" not in result
        assert result == "ひらがな"

    def test_empty_string(self):
        """Test empty string handling."""
        result = get_furigana("")
        assert result == ""

    def test_kanji_with_correct_furigana_format(self):
        """Test that furigana follows Anki format: 漢字[かんじ]"""
        result = get_furigana("学生")
        assert "学生[" in result
        assert "]" in result
        # Should be hiragana in brackets
        assert "がくせい" in result

    def test_particles_no_furigana(self):
        """Test that particles don't get furigana."""
        result = get_furigana("私は")
        # は should not get furigana
        parts = result.split()
        assert any("私[" in part for part in parts)


class TestGetTokenizer:
    """Tests for tokenizer singleton."""

    def test_tokenizer_singleton(self):
        """Test that get_tokenizer returns the same instance."""
        tokenizer1 = get_tokenizer()
        tokenizer2 = get_tokenizer()
        assert tokenizer1 is tokenizer2

    def test_tokenizer_is_functional(self):
        """Test that tokenizer can tokenize text."""
        tokenizer = get_tokenizer()
        tokens = list(tokenizer.tokenize("日本語"))
        assert len(tokens) > 0
