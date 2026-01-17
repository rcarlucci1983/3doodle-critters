"""
Download images from Google Drive and convert HEIC to PNG
"""
import os
import requests
from pathlib import Path

try:
    from PIL import Image
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    print("Installing required libraries...")
    os.system("pip install pillow pillow-heif")
    from PIL import Image
    import pillow_heif
    pillow_heif.register_heif_opener()

SCRIPT_DIR = Path(__file__).parent
IMAGES_DIR = SCRIPT_DIR / "images"
TEMP_DIR = SCRIPT_DIR / "temp_downloads"

IMAGES_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Google Drive file IDs and names from the 3D Creatures folder
DRIVE_FILES = [
    ("1rBncurE4kLHBH2HfPLu8QACdEWRLCs5l", "IMG_20260108_211812.heic"),
    ("1szgfG6wS8YSIKemg5OW_xmxnH_W_Ik_O", "IMG_20260108_211819.heic"),
    ("1iU7rMhkze2aY5LnSeGKVwh0PZb5epSiU", "IMG_20260108_211828_1.heic"),
    ("1mpQDkUlfIOj3C2iYGJ1kJTUBuX5Z21cY", "IMG_20260108_211828.heic"),
    ("1kddjy63Rk6wYHucdlPOjHwKXmcbKEzHA", "IMG_20260108_211843_5.heic"),
    ("17R24D0kdBwUmpXnF-SR4_457CEF0AKqL", "IMG_20260108_211843_4.heic"),
    ("18hs9Ooh4p8pisiGh_w1U0NMW7eRPrGDL", "IMG_20260108_211843_3.heic"),
    ("1HYSfI0cMA9D0QkOa3IGtvvsM-Ud5EiXp", "IMG_20260108_211843_2.heic"),
    ("1uYDKcblLQM_S7euEjsyKpPq8jdX6Vq5N", "IMG_20260108_211843_1.heic"),
    ("1hrxUULJlE5A2nr5K9Dlv5-PoFLleBwmN", "IMG_20260108_211843.heic"),
]

def download_from_drive(file_id, filename):
    """Download a file from Google Drive."""
    # Google Drive direct download URL
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    print(f"  Downloading {filename}...", end=" ")

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filepath = TEMP_DIR / filename
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("OK")
            return filepath
        else:
            print(f"Failed (HTTP {response.status_code})")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def convert_heic_to_png(heic_path, output_name=None):
    """Convert HEIC file to PNG."""
    try:
        img = Image.open(heic_path)

        if output_name is None:
            output_name = Path(heic_path).stem + ".png"

        output_path = IMAGES_DIR / output_name
        img.save(output_path, "PNG")
        print(f"  Converted: {output_name}")
        return output_path
    except Exception as e:
        print(f"  Error converting {heic_path}: {e}")
        return None

def convert_local_heic_files():
    """Convert any HEIC files already in the images or temp folder."""
    heic_files = list(TEMP_DIR.glob("*.heic")) + list(TEMP_DIR.glob("*.HEIC"))
    heic_files += list(IMAGES_DIR.glob("*.heic")) + list(IMAGES_DIR.glob("*.HEIC"))

    if not heic_files:
        print("  No HEIC files found to convert.")
        return []

    converted = []
    for heic_file in heic_files:
        result = convert_heic_to_png(heic_file)
        if result:
            converted.append(result)

    return converted

def main():
    print("\n" + "=" * 60)
    print("  3Doodle Critters - Image Downloader & Converter")
    print("=" * 60)

    print("\n  Options:")
    print("    [1] Download from Google Drive and convert to PNG")
    print("    [2] Convert existing HEIC files in temp/images folder")
    print("    [3] Exit")

    choice = input("\n  Enter choice (1-3): ").strip()

    if choice == "1":
        print("\n  Downloading images from Google Drive...")
        print("  (Note: Files must be publicly accessible or you must be signed in)\n")

        downloaded = []
        for file_id, filename in DRIVE_FILES:
            result = download_from_drive(file_id, filename)
            if result:
                downloaded.append(result)

        print(f"\n  Downloaded {len(downloaded)} files.")

        if downloaded:
            print("\n  Converting to PNG...")
            for heic_file in downloaded:
                convert_heic_to_png(heic_file)

        print(f"\n  Done! Check the 'images' folder for PNG files.")

    elif choice == "2":
        print("\n  Looking for HEIC files to convert...")
        converted = convert_local_heic_files()
        print(f"\n  Converted {len(converted)} files.")

    elif choice == "3":
        print("\n  Goodbye!\n")
        return

    # List resulting PNG files
    png_files = list(IMAGES_DIR.glob("*.png"))
    if png_files:
        print(f"\n  PNG files in images folder ({len(png_files)}):")
        for f in sorted(png_files):
            print(f"    - {f.name}")

if __name__ == "__main__":
    main()
