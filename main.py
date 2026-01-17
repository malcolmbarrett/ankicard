import sys
import os
import uuid
import genanki
from gtts import gTTS
from janome.tokenizer import Tokenizer
from deep_translator import GoogleTranslator
from openai import OpenAI

# --- Configuration ---
tokenizer = Tokenizer()
translator = GoogleTranslator(source="ja", target="en")

# Define the Anki Model (Note Type) to match your "Immersion Kit" structure
# Fields: Expression, English, Reading, Screenshot, Audio Sentence, ID
IMMERSION_KIT_MODEL = genanki.Model(
    1607392319,  # Random unique ID for the Model
    "Immersion Kit Generator",
    fields=[
        {"name": "Expression"},
        {"name": "English"},
        {"name": "Reading"},
        {"name": "Screenshot"},
        {"name": "Audio Sentence"},
        {"name": "ID"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div style="font-size: 30px;">{{Expression}}</div><br>{{Screenshot}}',
            "afmt": '{{FrontSide}}<hr id="answer"><div style="font-size: 20px;">{{English}}</div><br><div style="font-size: 20px;">{{Reading}}</div><br>{{Audio Sentence}}',
        },
    ],
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } img { max-width: 400px; }",
)

# Output directory for temporary media files
MEDIA_DIR = "anki_media"
os.makedirs(MEDIA_DIR, exist_ok=True)


def to_hiragana(katakana):
    """Helper to convert Katakana to Hiragana."""
    result = ""
    for char in katakana:
        code = ord(char)
        if 0x30A1 <= code <= 0x30F6:
            result += chr(code - 0x60)
        else:
            result += char
    return result


def get_furigana(text):
    """Parses Japanese text and returns Anki-style furigana: 漢字[かんじ]"""
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


def generate_image(prompt, filename):
    """Generates an image using DALL-E 3."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Skipping image (No OPENAI_API_KEY found).")
        return None

    client = OpenAI(api_key=api_key)
    print("Generating image with DALL-E 3...")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A simple, minimalist illustration representing: {prompt}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # Download the image
        import requests

        img_data = requests.get(image_url).content
        filepath = os.path.join(MEDIA_DIR, filename)
        with open(filepath, "wb") as handler:
            handler.write(img_data)
        return filepath
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None


def main(japanese_text):
    # 1. Setup IDs and Filenames
    # Note: genanki needs a unique deck ID
    deck_id = 2059400110
    deck = genanki.Deck(deck_id, "Generated Japanese Deck")

    unique_id = str(uuid.uuid4())[:8]
    audio_filename = f"anki_{unique_id}.mp3"
    image_filename = f"anki_{unique_id}.jpg"

    print(f"Processing: {japanese_text}")

    # 2. English Translation
    english_text = translator.translate(japanese_text)
    print(f"Translation: {english_text}")

    # 3. Furigana
    furigana_text = get_furigana(japanese_text)

    # 4. Generate Media
    # Audio
    audio_path = os.path.join(MEDIA_DIR, audio_filename)
    tts = gTTS(text=japanese_text, lang="ja", slow=False)
    tts.save(audio_path)

    # Image
    image_path = generate_image(english_text, image_filename)

    # List of media files to include in the package
    media_files = [audio_path]

    # Prepare Image Field
    if image_path:
        image_field = f'<img src="{image_filename}">'
        media_files.append(image_path)
    else:
        image_field = ""

    # 5. Create the Note
    my_note = genanki.Note(
        model=IMMERSION_KIT_MODEL,
        fields=[
            japanese_text,  # Expression
            english_text,  # English
            furigana_text,  # Reading
            image_field,  # Screenshot
            f"[sound:{audio_filename}]",  # Audio Sentence
            unique_id,  # ID
        ],
    )

    deck.add_note(my_note)

    # 6. Export Package
    output_file = f"japanese_card_{unique_id}.apkg"
    package = genanki.Package(deck)
    package.media_files = media_files

    package.write_to_file(output_file)
    print(f"Success! Created: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_text = " ".join(sys.argv[1:])
        main(user_text)
    else:
        print("Please provide a Japanese sentence.")
