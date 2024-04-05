#!/bin/bash
# The first command-line argument is the path to the 'fg' directory, should contain images with transparency
fg='/mnt/g/o/fg'
# The second command-line argument is the path to the 'bg' directory, should have the same number of images as 'fg'
bg='/mnt/g/o/bg'
# The third command-line argument is the output directory for the layered frames
out='/mnt/g/o/output'

translate=435
frame_start=1
frame_end=11592

# Create the output directory if it doesn't exist
mkdir -p $out
# Process each pair of frames
for ((frame=frame_start; frame<=frame_end; frame++)); do
    ffmpeg -i ${bg}/${frame_name} -i ${fg}/${frame_name} -filter_complex "[0:v]crop=iw-${translate}:ih:0:0,pad=iw+${translate}:ih:${translate}:0[bg]; [bg][1:v]overlay" -vframes 1 ${out}/${frame_name}
done
# Compile the layered frames into a video

ffmpeg -f image2 -framerate 24 -i ${out}/%04d.tif -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p /mnt/c/Users/trist/Desktop/outputDef.mp4
ffmpeg -f image2 -framerate 24 -i ${out}/%04d.tif -c:v prores_ks -profile:v 3 /mnt/c/Users/trist/Desktop/outputProres.mov