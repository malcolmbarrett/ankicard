from deep_translator import GoogleTranslator

_translator = None


def get_translator() -> GoogleTranslator:
    """Lazy-loaded singleton translator."""
    global _translator
    if _translator is None:
        _translator = GoogleTranslator(source="ja", target="en")
    return _translator


def translate_to_english(text: str) -> str:
    """Translate Japanese text to English."""
    return get_translator().translate(text)
