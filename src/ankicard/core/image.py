from openai import OpenAI
import requests
import os


def generate_image(
    prompt: str, output_path: str, api_key: str | None = None
) -> str | None:
    """Generates an image using DALL-E 3."""
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)

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
        img_data = requests.get(image_url).content
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as handler:
            handler.write(img_data)
        return output_path
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None
