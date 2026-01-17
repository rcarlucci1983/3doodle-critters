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
    ("1rBncurE4kLHBH2HfPLu8QACdEWRLCs5l", "creature_01.heic"),
    ("1szgfG6wS8YSIKemg5OW_xmxnH_W_Ik_O", "creature_02.heic"),
    ("1iU7rMhkze2aY5LnSeGKVwh0PZb5epSiU", "creature_03.heic"),
    ("1mpQDkUlfIOj3C2iYGJ1kJTUBuX5Z21cY", "creature_04.heic"),
    ("1kddjy63Rk6wYHucdlPOjHwKXmcbKEzHA", "creature_05.heic"),
    ("17R24D0kdBwUmpXnF-SR4_457CEF0AKqL", "creature_06.heic"),
    ("18hs9Ooh4p8pisiGh_w1U0NMW7eRPrGDL", "creature_07.heic"),
    ("1HYSfI0cMA9D0QkOa3IGtvvsM-Ud5EiXp", "creature_08.heic"),
    ("1uYDKcblLQM_S7euEjsyKpPq8jdX6Vq5N", "creature_09.heic"),
    ("1hrxUULJlE5A2nr5K9Dlv5-PoFLleBwmN", "creature_10.heic"),
]

def download_from_drive(file_id, filename):
    """Download a file from Google Drive."""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    print(f"  Downloading {filename}...", end=" ", flush=True)

    try:
        # First request to get confirmation token if needed
        session = requests.Session()
        response = session.get(url, stream=True)

        # Check for virus scan warning page (large files)
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                url = f"https://drive.google.com/uc?export=download&confirm={value}&id={file_id}"
                response = session.get(url, stream=True)
                break

        if response.status_code == 200:
            filepath = TEMP_DIR / filename
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Check if we got actual image data (not HTML error page)
            file_size = filepath.stat().st_size
            if file_size < 1000:  # Likely an error page
                print(f"Failed (got {file_size} bytes - likely access denied)")
                filepath.unlink()
                return None

            print(f"OK ({file_size // 1024} KB)")
            return filepath
        else:
            print(f"Failed (HTTP {response.status_code})")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def convert_heic_to_png(heic_path):
    """Convert HEIC file to PNG."""
    try:
        img = Image.open(heic_path)
        output_name = Path(heic_path).stem + ".png"
        output_path = IMAGES_DIR / output_name
        img.save(output_path, "PNG")
        print(f"  Converted: {output_name}")
        return output_path
    except Exception as e:
        print(f"  Error converting {heic_path}: {e}")
        return None

def main():
    print("\n" + "=" * 60)
    print("  Downloading and Converting Images from Google Drive")
    print("=" * 60 + "\n")

    downloaded = []
    for file_id, filename in DRIVE_FILES:
        result = download_from_drive(file_id, filename)
        if result:
            downloaded.append(result)

    print(f"\n  Downloaded {len(downloaded)} of {len(DRIVE_FILES)} files.\n")

    if downloaded:
        print("  Converting HEIC to PNG...\n")
        converted = []
        for heic_file in downloaded:
            result = convert_heic_to_png(heic_file)
            if result:
                converted.append(result)

        print(f"\n  Successfully converted {len(converted)} images!")

    # List resulting PNG files
    png_files = list(IMAGES_DIR.glob("*.png"))
    if png_files:
        print(f"\n  PNG files ready in images folder:")
        for f in sorted(png_files):
            size_kb = f.stat().st_size // 1024
            print(f"    - {f.name} ({size_kb} KB)")
    else:
        print("\n  No PNG files created. The Google Drive files may not be publicly accessible.")
        print("  Alternative: Download the files manually from Google Drive to the 'temp_downloads' folder,")
        print("  then run this script again.")

if __name__ == "__main__":
    main()
