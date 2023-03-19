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
    output_file = os.path.splitext(input_file)[0] + '.mp4'
    probe_command = [
            '/usr/lib/jellyfin-ffmpeg/ffprobe',
            '-v',
            'error',
            '-select_streams',
            'v:0',
            '-show_entries',
            'stream=codec_name',
            '-of',
            'default=noprint_wrappers=1:nokey=1',
            f'"{escaped_input_file}"'
    ]
    video_codec = subprocess.check_output(' '.join(probe_command), shell=True).strip()
    probe_command = [
            '/usr/lib/jellyfin-ffmpeg/ffprobe',
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
    valid_video_codecs = [b'h264', b'hevc']

    if video_codec in valid_video_codecs and audio_codec == b'aac':
        print(f'[{input_file}]: codecs are fully supported.')
    elif video_codec in valid_video_codecs and audio_codec != b'aac':
        print(f'[%s]: Converting to AAC audio...' % (input_file))
        if convert:
            command = ['/usr/lib/jellyfin-ffmpeg/ffmpeg', '-y', '-i', '%s' % input_file, '-c:v', 'copy', '-c:a', 'aac', '-c:s', 'copy', output_file]
            subprocess.call(command)
    elif video_codec not in valid_video_codecs and audio_codec == b'aac':
        print(f'[%s]: Converting to H.264 video...' % (input_file))
        if convert:
            command = ['/usr/lib/jellyfin-ffmpeg/ffmpeg', '-y', '-i', '%s' % input_file, '-c:v', 'libx264', '-c:a', 'copy', '-c:s', 'copy', output_file]
            subprocess.call(command)
    else:
        print(f'[%s]: Converting video and audio...' % (input_file))
        if convert:
            command = ['/usr/lib/jellyfin-ffmpeg/ffmpeg', '-y', '-i', '%s' % input_file, '-c:v', 'libx264', '-c:a', 'aac', '-c:s', 'copy', output_file]
            subprocess.call(command)


def is_valid_stream_order(stream_indexes):
    types_order = ['video', 'audio', 'subtitle']

    current_type = 0
    current_index = 0
    while current_index < len(stream_indexes):
        current_element_type = stream_indexes[current_index].split('|')[1]

        if current_element_type != types_order[current_type]:
            return False

        current_type += 1
        if current_type == len(types_order):
            break

        current_index += 1
    return True


def reorder_stream_indexes(input_file, reorder):
    print('[%s]: Checking stream order... ' % input_file)

    ffprobe_command = f'/usr/lib/jellyfin-ffmpeg/ffprobe -i "{input_file}" -show_entries stream=index,codec_type -of compact=p=0:nk=1 -loglevel quiet'
    output = subprocess.check_output(ffprobe_command, shell=True).decode() # output = ['0|video', '1|audio', '2|subtitle', '3|subtitle', '4|subtitle', '5|subtitle']
    stream_indexes = output.strip().split('\n')

    if not is_valid_stream_order(stream_indexes):
        print('[%s]: Stream index ordering is incorrect. Attempting to re-order...' % input_file)
        print('\n')

        if reorder:
            ffmpeg_command = f'/usr/lib/jellyfin-ffmpeg/ffmpeg -i "{input_file}" -c copy -movflags +faststart'
            for i in range(len(stream_indexes)):
                stream_type = subprocess.check_output(
                    f'/usr/lib/jellyfin-ffmpeg/ffprobe -i "{input_file}" -select_streams {i}:v -show_entries stream=codec_type -of default=nw=1:nk=1',
                    shell=True
                ).decode().strip()

                if stream_type == 'video':
                    ffmpeg_command += f' -map 0:v:{i}'
                elif stream_type == 'audio':
                    ffmpeg_command += f' -map 0:a:{i}'
                elif stream_type == 'subtitle':
                    ffmpeg_command += f' -map 0:s:{i}?'

                ffmpeg_command += f' {output_file}'
                subprocess.run(ffmpeg_command, shell=True)
    else:
        print('[%s]: Stream index ordering is correct.' % input_file)
        print('\n')


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='Directory to scan for and convert files')
    parser.add_argument('--convert-media', action='store_true', help='Converts media files to given format. Otherwise just prints what it would convert')
    parser.add_argument(
            '--reorder-streams',
            action='store_true',
            help='Re-orders the stream indexes if they do not follow convention (vid=0, aud=1 ...). Otherwise just prints what would be re-ordered'
    )
    parser.add_argument('--no-recursive-check', action='store_false', help='Only check the top level directory passed. Will not check files in subdirectories')
    parser.add_argument('--remove-input-file', action='store_true', help='Remove the input file after the conversions are complete')

    return parser.parse_args()


def check_files(directory, convert_media=False, reorder_streams=False, recursive=True):
    media_extensions = ['.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

    print('Scanning files in [%s]...' % directory)
    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if os.path.isdir(path) and recursive:
            check_files(path, convert_media)
        if os.path.isfile(path):
            extension = os.path.splitext(path)[1].lower()
            if extension not in media_extensions:
                continue
            else:
                convert_file(path, convert_media)
                #reorder_stream_indexes(path, reorder_streams)


def main():
    options = parse_commandline()

    check_files(options.directory, convert_media=options.convert_media, reorder_streams=options.reorder_streams, recursive=options.no_recursive_check)

    if options.remove_input_file:
        print('Removing input file. [%s]' % input_file)
        os.remove(input_file)


if __name__ == '__main__':
    main()
