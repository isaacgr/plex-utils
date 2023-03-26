import os
import sys
import subprocess
import shutil
import argparse

import os
import subprocess

def convert_file(input_file, convert):
    #escaped_input_file = input_file.replace("'", "'\\''")
    escaped_input_file = input_file
    output_file = os.path.splitext(input_file)[0] + '.mp3'
    probe_command = [
            'ffprobe',
            '-v',
            'error',
            '-select_streams',
            'a:0',
            '-show_entries',
            'stream=codec_name',
            '-of',
            'default=noprint_wrappers=1:nokey=1',
            f'"{escaped_input_file}"'
    ]
    audio_codec = subprocess.check_output(' '.join(probe_command), shell=True).strip()
    valid_audio_codecs = [b'mp3']

    if audio_codec in valid_audio_codecs:
        print(f'[{input_file}]: codecs are fully supported.')
    else:
        print(f'[%s]: Converting audio...' % (input_file))
        if convert:
            command = ['ffmpeg', '-y', '-i', '%s' % input_file, '-ab', '320k', '-map_metadata', '0', '-id3v2_version', '3', output_file]
            subprocess.call(command)


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='Directory to scan for and convert files')
    parser.add_argument('--convert-media', action='store_true', help='Converts media files to given format. Otherwise just prints what it would convert')
    parser.add_argument('--no-recursive-check', action='store_false', help='Only check the top level directory passed. Will not check files in subdirectories')
    parser.add_argument('--remove-input-file', action='store_true', help='Remove the input file after the conversions are complete')

    return parser.parse_args()


def check_files(directory, convert_media=False, recursive=True):
    media_extensions = ['.mp3', '.flac', '.aac']

    print('Scanning files in [%s]...' % directory)
    for file in os.listdir(directory):
        if file == 'iTunes':
            continue
        path = os.path.join(directory, file)
        if os.path.isdir(path) and recursive:
            check_files(path, convert_media)
        if os.path.isfile(path):
            extension = os.path.splitext(path)[1].lower()
            if extension not in media_extensions:
                continue
            else:
                convert_file(path, convert_media)


def main():
    options = parse_commandline()

    check_files(options.directory, convert_media=options.convert_media, recursive=options.no_recursive_check)

    if options.remove_input_file:
        print('Removing input file. [%s]' % input_file)
        os.remove(input_file)


if __name__ == '__main__':
    main()
