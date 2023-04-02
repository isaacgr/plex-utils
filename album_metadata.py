import os
import csv
import requests
import mutagen
from mutagen.easyid3 import EasyID3

# Define the Last.fm API key and URL
API_KEY = ""
API_URL = "http://ws.audioscrobbler.com/2.0/"

# Define the directory path containing the song files
directory_path = "./Library/Organized"

# Create a CSV file to store the changes
csv_file = open("changes.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Filename", "Title", "Artist", "Album"])

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    if ' - ' in filename:
        artist = filename.split('-')[0].strip()
        if '.mp3' in filename:
            title = filename.split('-')[1].split('.mp3')[0].strip()
        elif '.MP3' in filename:
            title = filename.split('-')[1].split('.MP3')[0].strip()
    else:
        continue
        # Load the song file and extract the artist and title metadata
        try:
            song_file = EasyID3(os.path.join(directory_path, filename))
            artist = song_file.get("artist", [""])[0]
            title = song_file.get("title", [""])[0]
        except mutagen.id3._util.ID3NoHeaderError:
            print(f'No ID3 tags for {filename}. Attempting to parse artist and title from filename')
            try:
                artist = filename.split('-')[0].strip()
                if '.mp3' in filename:
                    title = filename.split('-')[1].split('.mp3')[0].strip()
                elif '.MP3' in filename:
                    title = filename.split('-')[1].split('.MP3')[0].strip()
                meta = mutagen.File(os.path.join(directory_path, filename), easy=True)
                meta.add_tags()
                meta['title'] = title
                meta['artist'] = artist
                meta.save(os.path.join(directory_path, filename))
                song_file = EasyID3(os.path.join(directory_path, filename))
                artist = song_file.get("artist", [""])[0]
                title = song_file.get("title", [""])[0]
            except Exception as e:
                print(e)
                print('Nope.')
        artist = song_file.get("artist", [""])
        title = song_file.get("title", [""])

    params = {
        "method": "track.getInfo",
        "api_key": API_KEY,
        "artist": artist,
        "track": title,
        "autocorrect": 1,
        "format": "json"
    }

    # Make the request to the Last.fm API
    response = requests.get(API_URL, params=params)

    # Parse the response JSON and extract the album information
    response_json = response.json()
    artist = ""
    album = ""
    title = ""
    genre = ""
    try:
        title = response_json["track"]["name"]
    except KeyError:
        print(f"No title for {filename}")
    try:
        artist = response_json["track"]["album"]["artist"]
    except KeyError:
        try:
            artist = response_json["track"]["artist"]['name']
        except KeyError:
            print(f"No artist for {filename}")
    try:
        album = response_json["track"]["album"]["title"]
    except KeyError:
        print(f"No album for {filename}")
    try:
        genre = response_json["track"]["toptags"]["tag"][0]['name']
        genre = genre.capitalize()
    except (KeyError, IndexError):
        print(f"No genre found for {filename}")

    # Print the changes to the console
    print(f"Filename: {filename}, Title: {title}, Artist: {artist}, Album: {album}")

    # Write the changes to the CSV file
    csv_writer.writerow([filename, title, artist, album])

    # Add the album metadata to the song file and save the changes
    #song_file["album"] = album
    #song_file["title"] = title
    #song_file["artist"] = artist
    #song_file["genre"] = genre
    #song_file.save()

# Close the CSV file
csv_file.close()

