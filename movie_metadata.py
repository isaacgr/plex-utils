import os
import subprocess
import csv
import argparse
import math

def get_movie_metadata(filename):
    # Run ffprobe on the movie file
    streams_cmd = ["/usr/lib/jellyfin-ffmpeg/ffprobe", "-v", "error", "-show_entries", "stream=index,codec_type,codec_name,width,height,bit_rate", "-of", "csv=p=0", filename]
    streams_output = subprocess.check_output(streams_cmd).decode("utf-8").strip()

    format_cmd = ["/usr/lib/jellyfin-ffmpeg/ffprobe", "-v", "error", "-show_entries", "format=format_name", "-of", "csv=p=0", filename]
    format_output = subprocess.check_output(format_cmd).decode("utf-8").strip()

    # Parse the output and extract the metadata we're interested in
    video_format = None
    video_codec = None
    audio_codec = None
    video_bitrate = None
    audio_bitrate = None
    stream_order = []
    video_resolution = None

    for line in format_output.split('\n'):
        formats = '+'.join(line.strip('\"').split(','))
        video_format = formats

    for line in streams_output.split('\n'):
        if not line:
            continue
        parts = line.split(",")
        stream_index = parts[0]
        codec_type = parts[1]
        if codec_type in ['mjpeg']:
            continue
        codec_name = parts[2]
        bitrate = parts[-1]
        if codec_name.startswith("video"):
            video_codec = codec_type
            video_bitrate = bitrate
            video_resolution = f"{parts[3]}x{parts[4]}"
            stream_order.append(stream_index)
        elif codec_name.startswith("audio"):
            audio_codec = codec_type
            audio_bitrate = bitrate
            stream_order.append(stream_index)
    return (filename, video_format, video_codec, audio_codec, video_bitrate, audio_bitrate, ";".join(stream_order), video_resolution)

def write_to_csv(metadata_list, csv_filename):
    # Write the metadata to a CSV file
    with open(csv_filename, mode="w", newline="") as csv_file:
        fieldnames = ["Filename", "Video Format", "Video Codec", "Audio Codec", "Video Bitrate", "Audio Bitrate", "Stream Order", "Video Resolution"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for metadata in metadata_list:
            writer.writerow({
                "Filename": metadata[0],
                "Video Format": metadata[1],
                "Video Codec": metadata[2],
                "Audio Codec": metadata[3],
                "Video Bitrate": metadata[4],
                "Audio Bitrate": metadata[5],
                "Stream Order": metadata[6],
                "Video Resolution": metadata[7]
            })

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Recursively look through a directory and use ffprobe on movie files to determine their metadata.")
    parser.add_argument("directory", help="The directory to traverse.")
    parser.add_argument('--top-level-only', action='store_true', help='Only traverse the top level directory, no recursion')
    parser.add_argument('--deep-traversal', action='store_true', help='Only traverse the top level directory, no recursion')
    args = parser.parse_args()

    movie_files = []
    if args.top_level_only:
        for name in os.listdir(args.directory):
            if name.endswith(".mkv") or name.endswith(".mp4") or name.endswith(".avi"):
                movie_files.append(os.path.join(args.directory, name))
    else:
        for root, dirs, files in os.walk(args.directory, topdown=False):
            if args.deep_traversal or root.count(os.path.sep) <= args.directory.count(os.path.sep):
                for name in files:
                    if name.endswith(".mkv") or name.endswith(".mp4") or name.endswith(".avi"):
                        movie_files.append(os.path.join(root, name))
                                # add condition to check if depth of directory is greater than 1
        dirs[:] = [dir for dir in dirs if root.count(os.path.sep) - args.directory.count(os.path.sep) <= 1]

    # Collect metadata for each movie file
    metadata_list = []
    for movie_file in movie_files:
        metadata = get_movie_metadata(movie_file)
        metadata_list.append(metadata)

    # Write the metadata to a CSV file
    write_to_csv(metadata_list, "movie_metadata.csv")

if __name__ == "__main__":
    main()

