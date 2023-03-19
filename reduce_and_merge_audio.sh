#!/bin/bash

# Reduce the number of audio channels to 2 and add add as a second audio stream
ffmpeg -i "$1" -filter_complex "[0:a]asplit=6[FL][FR][FC][LFE][BL][BR];[FL]pan=stereo|c0=c0+c2|c1=c1+c3[FLmix];[FR]pan=stereo|c0=c0+c2|c1=c1+c3[FRmix];[FC]pan=stereo|c0=c0+c2|c1=c1+c3[FCmix];[LFE]pan=stereo|c0=c0+c2|c1=c1+c3[LFEmix];[BL]pan=stereo|c0=c0+c2|c1=c1+c3[BLmix];[BR]pan=stereo|c0=c0+c2|c1=c1+c3[BRmix];[FLmix][FRmix][FCmix][LFEmix][BLmix][BRmix]amerge=inputs=6[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -ac 2 "$2"
