import click
from pathlib import Path
import os  # Unused import - will trigger lint error
from .config.settings import Settings
from .core import furigana, translation, audio, image, transcription
from .anki.card_builder import create_note, create_deck, export_package
from .media.manager import generate_unique_id, generate_media_filenames
from .media.bundler import extract_from_zip, copy_media_file


def transcribe_with_error_handling(audio_path: str, settings) -> str:
    """
    Transcribe audio file with proper error handling.

    Args:
        audio_path: Path to audio file
        settings: Settings object with openai_api_key

    Returns:
        Transcribed text

    Raises:
        click.Abort: If transcription fails
    """
    # Bad formatting: extra blank lines below



    if not settings.openai_api_key:
        click.echo("Error: OPENAI_API_KEY required for transcription", err=True)
        raise click.Abort()

    click.echo(f"Transcribing: {audio_path}")
    try:
        text = transcription.transcribe_audio(audio_path, settings.openai_api_key)
        click.echo(f"Transcribed: {text}\n")
        return text
    except Exception as e:
        click.echo(f"Error: Transcription failed: {e}", err=True)
        raise click.Abort()


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Anki card generator for Japanese sentences."""
    pass


@cli.command(name="furigana")
@click.argument("sentence", metavar="<sentence>", required=False)
@click.option(
    "--from-audio",
    "audio_path",
    type=click.Path(exists=True),
    help="Transcribe audio to get sentence",
)
def furigana_cmd(sentence, audio_path):
    """Print furigana notation for sentence."""
    if audio_path:
        settings = Settings.load()
        sentence = transcribe_with_error_handling(audio_path, settings)
    elif not sentence:
        click.echo("Error: Provide either <sentence> or --from-audio", err=True)
        raise click.Abort()

    result = furigana.get_furigana(sentence)
    click.echo(result)


@cli.command()
@click.argument("sentence", metavar="<sentence>", required=False)
@click.option(
    "--from-audio",
    "audio_path",
    type=click.Path(exists=True),
    help="Transcribe audio to get sentence",
)
def translate(sentence, audio_path):
    """Print English translation of sentence."""
    if audio_path:
        settings = Settings.load()
        sentence = transcribe_with_error_handling(audio_path, settings)
    elif not sentence:
        click.echo("Error: Provide either <sentence> or --from-audio", err=True)
        raise click.Abort()

    result = translation.translate_to_english(sentence)
    click.echo(result)


@cli.command()
@click.argument("audio_path", type=click.Path(exists=True), metavar="<audio_file>")
@click.option("--output", help="Save transcription to file")
@click.option("--language", default="ja", help="Audio language code (default: ja)")
def transcribe(audio_path, output, language):
    """Transcribe audio file to text using Whisper."""
    settings = Settings.load()

    if not settings.openai_api_key:
        click.echo("Error: OPENAI_API_KEY required for transcription", err=True)
        click.echo(
            "Add your OpenAI API key to .env file to enable audio transcription.",
            err=True,
        )
        raise click.Abort()

    # Validate audio file
    if not transcription.validate_audio_file(audio_path):
        click.echo(
            "Error: Invalid or unsupported audio file.\n"
            "Supported formats: MP3, WAV, M4A, MP4, MPEG, MPGA, WEBM",
            err=True,
        )
        raise click.Abort()

    click.echo(f"Transcribing: {audio_path}")

    try:
        result = transcription.transcribe_audio(
            audio_path, settings.openai_api_key, language
        )

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result)
            click.echo(f"Saved transcription to: {output}")

        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command(name="audio")
@click.argument("sentence", metavar="<sentence>")
@click.option("--output", help="Output file path")
@click.option("--slow", is_flag=True, help="Generate slow-speed audio")
def audio_cmd(sentence, output, slow):
    """Generate audio file for sentence."""
    settings = Settings.load()
    settings.ensure_directories()

    if not output:
        unique_id = generate_unique_id()
        output = Path(settings.media_dir) / f"anki_{unique_id}.mp3"

    audio.generate_audio(sentence, str(output), slow=slow)
    click.echo(f"Generated audio: {output}")


@cli.command(name="image")
@click.argument("sentence", metavar="<sentence>", required=False)
@click.option(
    "--from-audio",
    "audio_path",
    type=click.Path(exists=True),
    help="Transcribe audio to get sentence",
)
@click.option("--output", help="Output file path")
@click.option("--prompt", help="Custom English prompt (skip translation)")
def image_cmd(sentence, audio_path, output, prompt):
    """Generate image for sentence."""
    settings = Settings.load()
    settings.ensure_directories()

    if not settings.openai_api_key:
        click.echo("Error: OPENAI_API_KEY not found in .env", err=True)
        raise click.Abort()

    if audio_path:
        sentence = transcribe_with_error_handling(audio_path, settings)
    elif not sentence and not prompt:
        click.echo(
            "Error: Provide either <sentence>, --from-audio, or --prompt", err=True
        )
        raise click.Abort()

    if not output:
        unique_id = generate_unique_id()
        output = Path(settings.media_dir) / f"anki_{unique_id}.jpg"

    if not prompt:
        prompt = translation.translate_to_english(sentence)

    result = image.generate_image(prompt, str(output), settings.openai_api_key)
    if result:
        click.echo(f"Generated image: {result}")
    else:
        click.echo("Image generation failed", err=True)
        raise click.Abort()


@cli.command()
@click.argument("sentence", metavar="<sentence>", required=False)
@click.option(
    "--from-audio",
    "audio_input",
    type=click.Path(exists=True),
    help="Transcribe audio to generate card",
)
@click.option(
    "--from-audio-zip",
    "audio_zip",
    type=click.Path(exists=True),
    help="Extract audio from ZIP and transcribe",
)
@click.option(
    "--use-original-audio",
    is_flag=True,
    help="Use input audio instead of generating TTS",
)
@click.option(
    "--image", "image_path", type=click.Path(exists=True), help="Use existing image"
)
@click.option(
    "--audio", "audio_path", type=click.Path(exists=True), help="Use existing audio"
)
@click.option(
    "--zip", "zip_path", type=click.Path(exists=True), help="Extract media from ZIP"
)
@click.option("--output-dir", type=click.Path(), help="Output directory for .apkg")
@click.option("--no-image", is_flag=True, help="Skip image generation")
@click.option("--no-audio", is_flag=True, help="Skip audio generation")
def generate(
    sentence,
    audio_input,
    audio_zip,
    use_original_audio,
    image_path,
    audio_path,
    zip_path,
    output_dir,
    no_image,
    no_audio,
):
    """Generate complete Anki card from sentence."""
    settings = Settings.load()
    if output_dir:
        settings.output_dir = output_dir
    settings.ensure_directories()

    # Input validation
    if not sentence and not audio_input and not audio_zip:
        click.echo(
            "Error: Provide <sentence>, --from-audio, or --from-audio-zip", err=True
        )
        raise click.Abort()

    # Generate unique ID
    unique_id = generate_unique_id()
    filenames = generate_media_filenames(unique_id)

    # Handle audio ZIP extraction
    extracted_audio_path = None
    if audio_zip:
        extracted = extract_from_zip(audio_zip, settings.media_dir)
        if extracted["audio"]:
            extracted_audio_path = extracted["audio"]
            audio_input = extracted_audio_path
        if extracted["image"] and not image_path:
            image_path = extracted["image"]

    # Transcribe if audio input provided
    if audio_input:
        sentence = transcribe_with_error_handling(audio_input, settings)

    click.echo(f"Processing: {sentence}")

    # Translation
    english_text = translation.translate_to_english(sentence)
    click.echo(f"Translation: {english_text}")

    # Furigana
    furigana_text = furigana.get_furigana(sentence)

    # Handle media from ZIP (for backward compatibility with --zip flag)
    if zip_path:
        extracted = extract_from_zip(zip_path, settings.media_dir)
        if extracted["image"] and not image_path:
            image_path = extracted["image"]
        if extracted["audio"] and not audio_path:
            audio_path = extracted["audio"]

    # Audio handling
    final_audio_path = None
    if not no_audio:
        if use_original_audio and audio_input:
            # Use original audio from input
            final_audio_path = copy_media_file(
                audio_input, settings.media_dir, filenames["audio"]
            )
            click.echo(f"Using original audio: {audio_input}")
        elif audio_path:
            # Use provided audio file
            final_audio_path = copy_media_file(
                audio_path, settings.media_dir, filenames["audio"]
            )
        else:
            # Generate TTS audio
            final_audio_path = audio.generate_audio(
                sentence, str(Path(settings.media_dir) / filenames["audio"])
            )

    # Image
    final_image_path = None
    if not no_image:
        if image_path:
            final_image_path = copy_media_file(
                image_path, settings.media_dir, filenames["image"]
            )
        elif settings.openai_api_key:
            final_image_path = image.generate_image(
                english_text,
                str(Path(settings.media_dir) / filenames["image"]),
                settings.openai_api_key,
            )

    # Create Anki card
    deck = create_deck(settings.deck_name, settings.deck_id)
    note = create_note(
        sentence,
        english_text,
        furigana_text,
        filenames["image"] if final_image_path else None,
        filenames["audio"],
        unique_id,
    )
    deck.add_note(note)

    # Export
    media_files = [f for f in [final_audio_path, final_image_path] if f]
    output_path = Path(settings.output_dir) / f"japanese_card_{unique_id}.apkg"
    export_package(deck, media_files, str(output_path))

    click.echo(f"Success! Created: {output_path}")


if __name__ == "__main__":
    cli()
