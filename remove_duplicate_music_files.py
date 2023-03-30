import os
import sys
import hashlib
from mutagen.easyid3 import EasyID3


def compute_md5(file_path):
    """Compute the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.digest()


def get_music_files(directory):
    """Get all music files in a directory."""
    music_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in (".mp3", ".flac", ".wav", ".m4a"):
                music_files.append(os.path.join(root, file))
    return music_files


def get_metadata(file_path):
    """Get metadata of a music file."""
    metadata = {"title": "", "artist": "", "album": "", "bitrate": ""}
    try:
        audio = EasyID3(file_path)
        metadata["title"] = audio["title"][0]
        metadata["artist"] = audio["artist"][0]
        metadata["album"] = audio["album"][0]
        metadata["bitrate"] = audio.info.bitrate
    except Exception:
        pass
    return metadata


def remove_duplicates(directory, delete_old_files=False):
    """Remove duplicate music files."""
    music_files = get_music_files(directory)
    file_groups = {}
    for file in music_files:
        metadata = get_metadata(file)
        key = metadata["title"]
        if key:
            if key not in file_groups:
                file_groups[key] = []
            file_groups[key].append((file, metadata))

    for key, files in file_groups.items():
        if len(files) > 1:
            best_file = None
            best_cost = None
            for file, metadata in files:
                cost = (
                    bool(metadata["title"]),
                    bool(metadata["artist"]),
                    bool(metadata["album"]),
                    metadata["bitrate"],
                )
                if best_file is None or cost > best_cost:
                    best_file = file
                    best_cost = cost

            for file, metadata in files:
                if file != best_file:
                    print(f"Removing {file}")
                    if delete_old_files:
                        os.remove(file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_duplicates.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    remove_duplicates(directory, delete_old_files=False)

