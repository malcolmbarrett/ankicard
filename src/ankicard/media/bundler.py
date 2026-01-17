import zipfile
import shutil
from pathlib import Path


def extract_from_zip(zip_path: str, output_dir: str) -> dict[str, str | None]:
    """Extract image and audio from ZIP."""
    result = {"image": None, "audio": None}

    with zipfile.ZipFile(zip_path, "r") as zf:
        for filename in zf.namelist():
            ext = Path(filename).suffix.lower()
            if ext in [".jpg", ".jpeg", ".png"] and not result["image"]:
                result["image"] = zf.extract(filename, output_dir)
            elif ext == ".mp3" and not result["audio"]:
                result["audio"] = zf.extract(filename, output_dir)

    return result


def copy_media_file(source_path: str, dest_dir: str, new_filename: str) -> str:
    """Copy media file with new filename."""
    dest_path = Path(dest_dir) / new_filename
    shutil.copy2(source_path, dest_path)
    return str(dest_path)
