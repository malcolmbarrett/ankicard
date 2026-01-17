"""Audio transcription using OpenAI Whisper API."""

from openai import OpenAI
from pathlib import Path


def transcribe_audio(
    audio_path: str,
    api_key: str | None = None,
    language: str = "ja",
    response_format: str = "text",
) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_path: Path to audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
        api_key: OpenAI API key
        language: ISO-639-1 language code (default: ja for Japanese)
        response_format: Response format (text, json, srt, verbose_json, vtt)

    Returns:
        Transcribed text string

    Raises:
        ValueError: If API key is missing
        FileNotFoundError: If the audio file does not exist
        Exception: If transcription fails
    """
    if not api_key:
        raise ValueError("OpenAI API key required for transcription")

    audio_file_path = Path(audio_path)
    if not audio_file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    client = OpenAI(api_key=api_key)

    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format=response_format,
            )

        # Handle different response formats
        if response_format == "text":
            return transcript.strip()
        else:
            return transcript.text.strip()

    except Exception as e:
        raise Exception(f"Transcription failed: {e}")


def validate_audio_file(audio_path: str) -> bool:
    """
    Validate that file exists and has supported audio extension.

    Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

    Args:
        audio_path: Path to audio file

    Returns:
        True if file is valid, False otherwise
    """
    supported_extensions = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}
    audio_file = Path(audio_path)

    if not audio_file.exists():
        return False

    return audio_file.suffix.lower() in supported_extensions
