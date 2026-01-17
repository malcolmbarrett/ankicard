from gtts import gTTS
import os


def generate_audio(
    text: str, output_path: str, lang: str = "ja", slow: bool = False
) -> str:
    """Generate TTS audio file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(output_path)
    return output_path
