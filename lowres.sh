#compiles folder of %04d.png frames into a mp4 video
out='./output'
ffmpeg -f image2 -framerate 24 -i ${out}/%04d.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4