#!/bin/bash

/usr/lib/jellyfin-ffmpeg/ffprobe -v quiet -print_format json -show_streams -show_format "$1"
