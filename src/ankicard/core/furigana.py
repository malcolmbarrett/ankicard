from janome.tokenizer import Tokenizer

_tokenizer = None


def get_tokenizer() -> Tokenizer:
    """Lazy-loaded singleton tokenizer."""
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = Tokenizer()
    return _tokenizer


def is_kanji(char: str) -> bool:
    """Check if a character is a kanji (CJK Unified Ideograph)."""
    return 0x4E00 <= ord(char) <= 0x9FFF


def to_hiragana(katakana: str) -> str:
    """Helper to convert Katakana to Hiragana."""
    result = ""
    for char in katakana:
        code = ord(char)
        if 0x30A1 <= code <= 0x30F6:
            result += chr(code - 0x60)
        else:
            result += char
    return result


def apply_furigana_to_token(surface: str, reading: str) -> str:
    """
    Apply furigana only to kanji portions of a word, leaving kana as-is.

    Args:
        surface: The word as it appears (e.g., "厳しい")
        reading: The reading in katakana (e.g., "キビシイ")

    Returns:
        Formatted furigana string (e.g., "厳[きび]しい")
    """
    hiragana_reading = to_hiragana(reading)

    # Find trailing kana (okurigana)
    trailing_kana = ""
    for i in range(len(surface) - 1, -1, -1):
        if not is_kanji(surface[i]):
            trailing_kana = surface[i] + trailing_kana
        else:
            break

    # Find leading kana (prefixes like お, ご)
    leading_kana = ""
    first_kanji_idx = 0
    for i, char in enumerate(surface):
        if not is_kanji(char):
            leading_kana += char
        else:
            first_kanji_idx = i
            break

    # Extract kanji portion
    kanji_end = len(surface) - len(trailing_kana)
    kanji_portion = surface[first_kanji_idx:kanji_end]

    # Check if word has no kanji
    if not any(is_kanji(c) for c in surface):
        return surface

    # Map reading segments
    reading_start = len(leading_kana)
    reading_end = len(hiragana_reading) - len(trailing_kana)

    # Validate reading matches surface kana
    if trailing_kana and not hiragana_reading.endswith(trailing_kana):
        # Fallback: entire word gets furigana
        return f"{surface}[{hiragana_reading}]"

    if leading_kana and not hiragana_reading.startswith(leading_kana):
        # Fallback: entire word gets furigana
        return f"{surface}[{hiragana_reading}]"

    kanji_reading = hiragana_reading[reading_start:reading_end]

    return f"{leading_kana}{kanji_portion}[{kanji_reading}]{trailing_kana}"


def get_furigana(text: str) -> str:
    """Parses Japanese text and returns Anki-style furigana: 漢字[かんじ]"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(text)
    result = ""
    for token in tokens:
        surface = token.surface
        reading = token.reading
        if reading != "*" and reading != surface:
            hiragana_reading = to_hiragana(reading)
            if surface != hiragana_reading:
                result += f" {apply_furigana_to_token(surface, reading)}"
            else:
                result += surface
        else:
            result += surface
    return result.strip()
