# Anki Japanese Sentence Card Generator

[![CI](https://github.com/malcolmbarrett/ankicard/workflows/CI/badge.svg)](https://github.com/malcolmbarrett/ankicard/actions)

A modular CLI tool for generating rich media Anki cards from Japanese sentences. It automatically creates English translations, adds furigana readings, generates text-to-speech audio, and produces AI-generated illustrations. The final output is an `.apkg` file that can be imported directly into Anki.

The cards follow the exact format used by [Immersion Kit](https://www.immersionkit.com/). This makes the tool useful for creating consistent cards for sentences found on [Tatoeba](https://tatoeba.org/) or other sources that are missing from the Immersion Kit or [Nadeshiko](https://nadeshiko.co/) databases.

## Installation

Ensure you have `uv` installed, then install the CLI tool:

```bash
# Using make
make install

# Or directly with uv
uv tool install .
```

This makes the `ankicard` command available globally.

## Configuration

Create a `.env` file in your working directory with your OpenAI API key to enable image generation and audio transcription:

```
OPENAI_API_KEY=your-key-here
```

Image generation and audio transcription are optional - the tool will skip these features if no API key is provided.

## Audio Transcription

The tool includes audio transcription powered by OpenAI's Whisper API. This enables:
- Creating Anki cards directly from audio recordings
- Extracting Japanese text without manual typing
- Using original audio recordings instead of TTS

**Requirements:** Set `OPENAI_API_KEY` in your `.env` file.

**Supported formats:** MP3, WAV, M4A, MP4, MPEG, MPGA, WEBM

## Usage

### Generate Complete Cards

Create a full Anki card with translation, furigana, audio, and image:

```bash
ankicard generate "中国でも戦国時代の墳墓からガラスが出土している。"
```

#### Options

- `--from-audio PATH` - Transcribe audio file to generate card
- `--from-audio-zip PATH` - Extract audio from ZIP and transcribe
- `--use-original-audio` - Use input audio instead of generating TTS
- `--image PATH` - Use an existing image file instead of generating
- `--audio PATH` - Use an existing audio file instead of generating
- `--zip PATH` - Extract image and audio from a ZIP bundle
- `--no-image` - Skip image generation
- `--no-audio` - Skip audio generation
- `--output-dir PATH` - Custom output directory (default: `anki_cards/`)

#### Examples

```bash
# From text (traditional usage)
ankicard generate "中国でも戦国時代の墳墓からガラスが出土している。"

# Skip image generation
ankicard generate "こんにちは" --no-image

# Use existing media files
ankicard generate "ありがとう" --image custom.jpg --audio custom.mp3

# Extract media from ZIP
ankicard generate "さようなら" --zip media_bundle.zip

# From audio file (transcribe automatically)
ankicard generate --from-audio recording.mp3

# Use original audio instead of TTS
ankicard generate --from-audio recording.mp3 --use-original-audio

# From ZIP with audio + screenshot
ankicard generate --from-audio-zip bundle.zip

# Audio + existing image
ankicard generate --from-audio recording.mp3 --image screenshot.jpg
```

### Individual Component Commands

Use components separately for custom workflows:

#### Transcribe Audio

Extract Japanese text from audio files:

```bash
ankicard transcribe recording.mp3
# Output: 中国でも戦国時代の墳墓からガラスが出土している。

# Save to file
ankicard transcribe recording.mp3 --output transcript.txt

# Specify language (default: ja)
ankicard transcribe recording.mp3 --language ja
```

#### Furigana

Print furigana notation to console:

```bash
# From text
ankicard furigana "日本語"
# Output: 日本語[にほんご]

# From audio
ankicard furigana --from-audio recording.mp3
```

#### Translation

Translate Japanese text to English:

```bash
# From text
ankicard translate "こんにちは"
# Output: Hello

# From audio
ankicard translate --from-audio recording.mp3
```

#### Audio

Generate audio file only:

```bash
ankicard audio "ありがとう"
# Output: Generated audio: anki_media/anki_XXXXX.mp3

# With options
ankicard audio "難しい文章" --slow --output custom.mp3
```

#### Image

Generate image only (requires OpenAI API key):

```bash
# From text
ankicard image "桜の木"
# Output: Generated image: anki_media/anki_XXXXX.jpg

# From audio
ankicard image --from-audio recording.mp3

# With custom prompt
ankicard image "猫" --prompt "A cute cartoon cat"
```

## Output

- Anki cards: `anki_cards/japanese_card_XXXXX.apkg`
- Media files: `anki_media/anki_XXXXX.{mp3,jpg}`

Import the `.apkg` files directly into Anki.

## Development

### Testing

The project includes a comprehensive test suite:

```bash
# Run tests
make test

# Run tests with coverage report
make test-cov
```

Or use pytest directly:

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=src/ankicard --cov-report=term-missing
```

### Code Quality

This project uses Ruff for linting and formatting.

**Linting:**

```bash
# Check for lint issues
make lint

# Auto-fix lint issues where possible
make lint-fix
```

**Formatting:**

```bash
# Format code
make format

# Check if code is formatted (without making changes)
make format-check
```

**Running All Checks:**

```bash
# Run lint, format-check, and tests
make check
```

These checks are also run automatically in CI via GitHub Actions.

### Makefile Targets

The project includes a Makefile for common tasks:

```bash
make help          # Show all available targets
make install       # Install the CLI tool globally
make reinstall     # Reinstall after code changes
make uninstall     # Uninstall the CLI tool
make test          # Run all tests
make test-cov      # Run tests with coverage report
make lint          # Run ruff linter
make lint-fix      # Run ruff linter with auto-fix
make format        # Format code with ruff
make format-check  # Check if code is formatted
make check         # Run all checks (lint, format-check, test)
make clean         # Remove all generated files
make clean-media   # Remove only media files
make clean-cards   # Remove only card files
make version       # Show installed version
```
