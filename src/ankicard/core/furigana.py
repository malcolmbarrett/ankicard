from janome.tokenizer import Tokenizer

_tokenizer = None


def get_tokenizer() -> Tokenizer:
    """Lazy-loaded singleton tokenizer."""
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = Tokenizer()
    return _tokenizer


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
                result += f" {surface}[{hiragana_reading}]"
            else:
                result += surface
        else:
            result += surface
    return result.strip()
