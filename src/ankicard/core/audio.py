import os
import shutil
import subprocess
import tempfile
import time

import requests
from gtts import gTTS
from openai import OpenAI


def is_docker_running() -> bool:
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def detect_container_runtime() -> str:
    """Detect if 'docker' is actually podman. Returns 'podman' or 'docker'."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if "podman" in result.stdout.lower():
            return "podman"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "docker"


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg is installed and available on PATH."""
    return shutil.which("ffmpeg") is not None


def is_voicevox_available(base_url: str = "http://127.0.0.1:50021") -> bool:
    """Check if VOICEVOX engine is running and reachable."""
    try:
        response = requests.get(f"{base_url}/version", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


def start_voicevox_docker(
    base_url: str = "http://127.0.0.1:50021",
    timeout: int = 60,
) -> bool:
    """
    Attempt to start the VOICEVOX Docker container.

    Tries to start an existing stopped container first, then falls back
    to creating a new one. Polls the health endpoint until ready.

    Args:
        base_url: VOICEVOX engine URL for health checking
        timeout: Maximum seconds to wait for engine to be ready

    Returns:
        True if engine is ready, False if start failed
    """
    # Check Docker daemon is running
    if not is_docker_running():
        return False

    # Try starting existing container
    result = subprocess.run(
        ["docker", "start", "voicevox"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # No existing container, create a new one
        result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "voicevox",
                "-p",
                "127.0.0.1:50021:50021",
                "--restart",
                "unless-stopped",
                "voicevox/voicevox_engine:cpu-latest",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False

    # Poll until engine is ready
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_voicevox_available(base_url):
            return True
        time.sleep(2)

    return False


def generate_audio_voicevox(
    text: str,
    output_path: str,
    base_url: str = "http://127.0.0.1:50021",
    speaker_id: int = 13,
    speed: float = 0.95,
) -> str:
    """
    Generate TTS audio file using VOICEVOX engine.

    Uses a two-step synthesis process: audio query creation followed by
    WAV synthesis, then converts to MP3 for Anki compatibility.

    Args:
        text: Japanese text to synthesize
        output_path: Path to save MP3 file
        base_url: VOICEVOX engine URL
        speaker_id: VOICEVOX speaker ID (default: 13, 青山龍星)
        speed: Speed scale (default: 0.95 for learner-friendly pacing)

    Returns:
        Path to generated MP3 audio file

    Raises:
        Exception: If audio generation fails
    """
    if not is_ffmpeg_available():
        raise Exception("ffmpeg is not installed. Install it with: brew install ffmpeg")

    try:
        dirname = os.path.dirname(output_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # Step 1: Create audio query
        query_response = requests.post(
            f"{base_url}/audio_query",
            params={"speaker": speaker_id, "text": text},
            timeout=30,
        )
        query_response.raise_for_status()
        audio_query = query_response.json()

        # Apply learner-friendly settings
        audio_query["speedScale"] = speed
        audio_query["intonationScale"] = 1.2
        audio_query["prePhonemeLength"] = 0.3
        audio_query["postPhonemeLength"] = 0.5

        # Step 2: Synthesize audio (returns WAV bytes)
        synth_response = requests.post(
            f"{base_url}/synthesis",
            params={"speaker": speaker_id},
            json=audio_query,
            timeout=60,
        )
        synth_response.raise_for_status()

        # Step 3: Convert WAV to MP3 via ffmpeg
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(synth_response.content)
            tmp_wav_path = tmp.name

        try:
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    tmp_wav_path,
                    output_path,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")
        finally:
            os.unlink(tmp_wav_path)

        return output_path
    except Exception as e:
        raise Exception(f"VOICEVOX TTS failed: {e}") from e


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
