import click
from pathlib import Path
from .config.settings import Settings
from .core import furigana, translation, audio, image
from .anki.card_builder import create_note, create_deck, export_package
from .media.manager import generate_unique_id, generate_media_filenames
from .media.bundler import extract_from_zip, copy_media_file


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Anki card generator for Japanese sentences."""
    pass


@cli.command(name="furigana")
@click.argument("sentence", metavar="<sentence>")
def furigana_cmd(sentence):
    """Print furigana notation for sentence."""
    result = furigana.get_furigana(sentence)
    click.echo(result)


@cli.command()
@click.argument("sentence", metavar="<sentence>")
def translate(sentence):
    """Print English translation of sentence."""
    result = translation.translate_to_english(sentence)
    click.echo(result)


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
@click.argument("sentence", metavar="<sentence>")
@click.option("--output", help="Output file path")
@click.option("--prompt", help="Custom English prompt (skip translation)")
def image_cmd(sentence, output, prompt):
    """Generate image for sentence."""
    settings = Settings.load()
    settings.ensure_directories()

    if not settings.openai_api_key:
        click.echo("Error: OPENAI_API_KEY not found in .env", err=True)
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
@click.argument("sentence", metavar="<sentence>")
@click.option("--image", "image_path", type=click.Path(exists=True), help="Use existing image")
@click.option("--audio", "audio_path", type=click.Path(exists=True), help="Use existing audio")
@click.option("--zip", "zip_path", type=click.Path(exists=True), help="Extract media from ZIP")
@click.option("--output-dir", type=click.Path(), help="Output directory for .apkg")
@click.option("--no-image", is_flag=True, help="Skip image generation")
@click.option("--no-audio", is_flag=True, help="Skip audio generation")
def generate(sentence, image_path, audio_path, zip_path, output_dir, no_image, no_audio):
    """Generate complete Anki card from sentence."""
    settings = Settings.load()
    if output_dir:
        settings.output_dir = output_dir
    settings.ensure_directories()

    # Generate unique ID
    unique_id = generate_unique_id()
    filenames = generate_media_filenames(unique_id)

    click.echo(f"Processing: {sentence}")

    # Translation
    english_text = translation.translate_to_english(sentence)
    click.echo(f"Translation: {english_text}")

    # Furigana
    furigana_text = furigana.get_furigana(sentence)

    # Handle media from ZIP
    if zip_path:
        extracted = extract_from_zip(zip_path, settings.media_dir)
        if extracted["image"] and not image_path:
            image_path = extracted["image"]
        if extracted["audio"] and not audio_path:
            audio_path = extracted["audio"]

    # Audio
    final_audio_path = None
    if not no_audio:
        if audio_path:
            final_audio_path = copy_media_file(audio_path, settings.media_dir, filenames["audio"])
        else:
            final_audio_path = audio.generate_audio(
                sentence, str(Path(settings.media_dir) / filenames["audio"])
            )

    # Image
    final_image_path = None
    if not no_image:
        if image_path:
            final_image_path = copy_media_file(image_path, settings.media_dir, filenames["image"])
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
