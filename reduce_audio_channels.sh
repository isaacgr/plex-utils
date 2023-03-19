#!/bin/bash

# reduce the number of audio channels to 2
ffmpeg -i "$1" -map 0:v -map 0:a -filter:a "pan=stereo|FL<FL+0.5*FC+0.5*BL|FR<FR+0.5*FC+0.5*BR" -c:v copy -c:a aac -b:a 256k -ac 2 "$2"

