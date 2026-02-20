from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class Settings:
    media_dir: str = "anki_media"
    output_dir: str = "anki_cards"
    openai_api_key: str | None = None
    voicevox_url: str = "http://127.0.0.1:50021"
    voicevox_speaker_id: int = 13
    deck_id: int = 2059400110
    deck_name: str = "Immersion Kit"

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv()
        return cls(
            media_dir=os.getenv("MEDIA_DIR", "anki_media"),
            output_dir=os.getenv("OUTPUT_DIR", "anki_cards"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            voicevox_url=os.getenv("VOICEVOX_URL", "http://127.0.0.1:50021"),
            voicevox_speaker_id=int(os.getenv("VOICEVOX_SPEAKER_ID", "13")),
        )

    def ensure_directories(self):
        os.makedirs(self.media_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
