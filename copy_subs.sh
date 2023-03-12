#!/bin/bash

/usr/lib/jellyfin-ffmpeg/ffmpeg -i "$1" -i "$2" -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng "$3"
