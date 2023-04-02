import os
import sys
import json
import shutil
import subprocess

# directory to search for music files
music_dir = "./Library/Downloads/Grunge, Rock & Punk - Karaoke - CDG"

# dictionary to store artist and album names
metadata_dict = {}

def get_metadata_tags(metadata):
    artist = metadata['tags'].get('artist', None)
    title = metadata['tags'].get('title', None)
    album = metadata['tags'].get('album', None)

    if not artist or not title:
        title = metadata['tags'].get('TITLE', None)
        artist = metadata['tags'].get('ARTIST', None)
        album = metadata['tags'].get('ALBUM', None)

    if not artist or not title:
        title = metadata['tags'].get('Title', None)
        artist = metadata['tags'].get('Artist', None)
        album = metadata['tags'].get('Album', None)

    if album == title:
        album = None

    if not artist or not title:
        raise Exception('No artist or title found')

    if ';' in artist:
        artist = artist.split(';')[0].strip()
    elif '/' in artist:
        artist = artist.split('/')[0].strip()

    return (artist, album, title)


# recursive function to search for music files
def search_dir(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # check if file is a music file (mp3, wav, etc.)
            if any(ext in filename for ext in ['.mp3', '.flac']):
                filepath = os.path.join(root, filename)
                # use ffprobe to get metadata
                try:
                    result = subprocess.check_output(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", filepath]).decode('utf-8').strip()
                except subprocess.CalledProcessError:
                    print(f'Cant parse {filepath}')
                    continue
                # parse metadata and add to dictionary
                try:
                    result = json.loads(result)
                    metadata = result["format"]
                    artist, album, title = get_metadata_tags(metadata)
                    metadata_dict.setdefault(artist, {})
                    if album:
                        metadata_dict[artist].setdefault(album, [])
                        # check for duplicates based on title and artist
                        if title in [
                            song[0]
                            for album, songs in metadata_dict[artist].items()
                            for song in songs
                            ]:
                            pass
                            #print(f"Duplicate file found: {filepath}")
                        else:
                            metadata_dict[artist][album].append([title, filepath])
                    else:
                        # check for duplicates based on title and artist
                        metadata_dict[artist].setdefault('Unknown', [])
                        if title in [
                            song[0]
                            for song in metadata_dict[artist]
                            ]:
                            pass
                            #print(f"Duplicate file found: {filepath}")
                        else:
                            metadata_dict[artist]['Unknown'].append([title, filepath])
                except Exception as e:
                    #import pdb
                    #pdb.set_trace()
                    print(f"Error parsing metadata for file: {filepath}. [{e}]")

        for directory in dirs:
            search_dir(os.path.join(root, directory))

# create directories for artists and albums and move files
def create_directories():
#    for artist in metadata_dict:
#        if artist[-1] == '.':
#            artist = artist[:-1]
#        artist_dir = os.path.join('%s/Organized' % music_dir, artist)
#        os.makedirs(artist_dir, exist_ok=True)
#        if isinstance(metadata_dict[artist], dict):
#            for album in metadata_dict[artist]:
#                if album[-1] == '.':
#                    album = album[:-1]
#                album_dir = os.path.join(artist_dir, album)
#                os.makedirs(album_dir, exist_ok=True)
#                for song in metadata_dict[artist][album]:
#                    title, filename = song
#                    title = title.replace('/', '_')
#                    base_name, ext = os.path.splitext(filename)
#                    new_name = f'{title}{ext}'
#                    new_path = os.path.join(album_dir, new_name)
#                    shutil.copy(filename, new_path)
#        else:
    for artist in metadata_dict:
        for album, songs in metadata_dict[artist].items():
            for song in songs:
                title, filename = song
                title = title.replace('/', '_')
                base_name, ext = os.path.splitext(filename)
                new_name = f'{title}{ext}'
                new_path = os.path.join('./Library/Organized', new_name)
                shutil.copy(filename, new_path)

# call search_dir function to get metadata and create dictionary
search_dir(music_dir)

with open('metadata.txt', 'w') as f:
    f.write(json.dumps(metadata_dict, indent=2))

# create directories and move files
create_directories()

