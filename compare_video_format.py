import subprocess
import sys
import json

def get_video_info(filename):
    """
    Returns a dictionary containing information about the video file.
    Uses FFprobe tool to extract video information.
    """
    cmd = ['/usr/lib/jellyfin-ffmpeg/ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', filename]
    output = subprocess.check_output(cmd)
    video_info = json.loads(output.decode('utf-8'))
    return video_info


def write_to_file(video_info, filename):
    """
    Writes the video information to a file in JSON format.
    """
    with open(filename, 'w') as f:
        json.dump(video_info, f, indent=4)


def compare_video_format(file1, file2):
    """
    Compares the video format of two media files and identifies any differences in container, encoding, bitrate, etc.
    """
    info1 = get_video_info(file1)
    info2 = get_video_info(file2)

    # Write video info to files
    write_to_file(info1, 'video1_info.json')
    write_to_file(info2, 'video2_info.json')

if __name__ == '__main__':
    compare_video_format(sys.argv[1], sys.argv[2])
