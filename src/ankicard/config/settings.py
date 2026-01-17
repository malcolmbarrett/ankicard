from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class Settings:
    media_dir: str = "anki_media"
    output_dir: str = "anki_cards"
    openai_api_key: str | None = None
    deck_id: int = 2059400110
    deck_name: str = "Immersion Kit"

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv()
        return cls(
            media_dir=os.getenv("MEDIA_DIR", "anki_media"),
            output_dir=os.getenv("OUTPUT_DIR", "anki_cards"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

    def ensure_directories(self):
        os.makedirs(self.media_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
