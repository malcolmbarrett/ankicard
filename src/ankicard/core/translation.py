from deep_translator import GoogleTranslator
from openai import OpenAI

_translator = None


def get_translator() -> GoogleTranslator:
    """Lazy-loaded singleton translator."""
    global _translator
    if _translator is None:
        _translator = GoogleTranslator(source="ja", target="en")
    return _translator


def translate_to_english(text: str) -> str:
    """Translate Japanese text to English using Google Translate."""
    return get_translator().translate(text)


def translate_to_english_openai(
    text: str, api_key: str | None = None, model: str = "gpt-4o-mini"
) -> str:
    """
    Translate Japanese text to English using OpenAI Chat API.

    Args:
        text: Japanese text to translate
        api_key: OpenAI API key
        model: Model to use (gpt-4o-mini, gpt-4o, etc.)

    Returns:
        English translation

    Raises:
        ValueError: If API key is missing
        Exception: If translation fails
    """
    if not api_key:
        raise ValueError("OpenAI API key required for translation")

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a translator. Translate the following Japanese text to English. Provide only the translation, no explanations.",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.3,
        )
        translation = response.choices[0].message.content
        if translation is None:
            raise Exception("OpenAI returned empty translation")
        return translation.strip()
    except Exception as e:
        raise Exception(f"OpenAI translation failed: {e}") from e
