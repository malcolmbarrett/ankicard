from google import genai
from google.genai import types
import os


def generate_image(
    prompt: str, output_path: str, api_key: str | None = None
) -> str | None:
    """Generates an image using Google Gemini."""
    if not api_key:
        return None

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=(
                f"Create an illustration for a language learning flashcard that "
                f"visually represents: {prompt}\n\n"
                f"Choose an art style that fits the mood and subject of the "
                f"sentence — for example, anime for everyday life, watercolor "
                f"for nature, pixel art for games, noir for mystery, etc. "
                f"Use your judgment.\n\n"
                f"Small amounts of text are fine if natural to the scene "
                f"(signs, labels, speech bubbles), but do not write out the "
                f"full sentence or caption."
            ),
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
        if response.parts:
            for part in response.parts:
                if part.inline_data is not None:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    part.as_image().save(output_path)
                    return output_path
        print("Image generation failed: no image in response")
        return None
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None
