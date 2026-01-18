from gtts import gTTS
from openai import OpenAI
import os


def enhance_text_for_speech(text: str, api_key: str) -> str:
    """
    Enhance Japanese text for more natural TTS output.

    Uses ChatGPT to add natural pauses and phrasing to Japanese text
    to make it sound more natural when read aloud by a TTS system.

    Args:
        text: Japanese text to enhance
        api_key: OpenAI API key

    Returns:
        Enhanced text optimized for TTS, or original text if enhancement fails
    """
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in Japanese phonetics and text-to-speech optimization. Your task is to add natural pauses and phrasing to Japanese text to make it sound more natural when read aloud by a TTS system. Add Japanese punctuation marks (、。) where a native speaker would naturally pause. Do NOT change any of the original Japanese characters - only add punctuation for natural phrasing. Return ONLY the enhanced Japanese text with no explanations.",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        enhanced = response.choices[0].message.content
        if enhanced is None:
            return text
        return enhanced.strip()
    except Exception:
        # Fall back to original text if enhancement fails
        return text


def generate_audio(
    text: str, output_path: str, lang: str = "ja", slow: bool = False
) -> str:
    """Generate TTS audio file using gTTS."""
    dirname = os.path.dirname(output_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(output_path)
    return output_path


def generate_audio_openai(
    text: str,
    output_path: str,
    api_key: str | None = None,
    model: str = "tts-1",
    voice: str = "alloy",
    speed: float = 1.0,
    enhance: bool = False,
) -> str:
    """
    Generate TTS audio file using OpenAI TTS API.

    Args:
        text: Japanese text to synthesize
        output_path: Path to save MP3 file
        api_key: OpenAI API key
        model: TTS model ("tts-1" or "tts-1-hd")
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        speed: Playback speed (0.25 to 4.0)
        enhance: Enhance text for natural speech (default: False)

    Returns:
        Path to generated audio file

    Raises:
        ValueError: If API key is missing
        Exception: If audio generation fails
    """
    if not api_key:
        raise ValueError("OpenAI API key required for TTS generation")

    try:
        dirname = os.path.dirname(output_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # Enhance text for better pronunciation if requested
        speech_text = enhance_text_for_speech(text, api_key) if enhance else text

        client = OpenAI(api_key=api_key)

        with client.audio.speech.with_streaming_response.create(
            model=model, voice=voice, input=speech_text, speed=speed
        ) as response:
            response.stream_to_file(output_path)

        return output_path
    except Exception as e:
        raise Exception(f"OpenAI TTS failed: {e}") from e
