out='/mnt/g/gink/mapplacer/o/output'
secondLocation='/mnt/c/Users/trist/Desktop/tempOut'
frame_start=1
frame_end=11592
min_size=15728640 # 15 MB in bytes

# report on missing .tif frames or frames under 15 MB in the range
# for every frame, check if the file exists and its size
# if we find one, start a range
# if the next frame is not missing and its size is not under 15 MB, end the range and print it

# initialize range
range_start=0
range_end=0

# list to save the start of ranges for ffmpeg
# Found in second location: 5685-5795
# Found in second location: 8488-8693
# Found in second location: 11370-11592
ranges=(5685 8488 11370)
rangee=(5795 8693 11592)

# for i in $(seq -f "%04g" $frame_start $frame_end); do
#   if [ ! -f $out/$i.tif ] || [ $(stat -c%s $out/$i.tif) -lt $min_size ]; then
#     if [ $range_start -eq 0 ]; then
#       range_start=$i
#     fi
#     range_end=$i
#   else
#     if [ $range_start -ne 0 ]; then
#       echo "Problematic frames: $range_start-$range_end"
#       #look for entire range in second location and print if found
#       yes=true
#       for j in $(seq -f "%04g" $range_start $range_end); do
#         if [ ! -f $secondLocation/$j.tif ] || [ $(stat -c%s $secondLocation/$j.tif) -lt $min_size ]; then
#           yes=false
#           break
#         fi        
#       done

#       if [ $yes = true ]; then
#         echo "Found in second location: $range_start-$range_end"
#         ranges+=($range_start)
#         rangee+=($range_end)
#       fi
#       range_start=0
#       range_end=0
#     fi
#   fi
# done

# # check if there is a remaining range of problematic frames
# if [ $range_start -ne 0 ]; then
#   echo "Problematic frames: $range_start-$range_end"
# fi
# # check if there is a remaining range at second location
# if [ $range_start -ne 0 ]; then
#   yes=true
#   for j in $(seq -f "%04g" $range_start $range_end); do
#     if [ ! -f $secondLocation/$j.tif ] || [ $(stat -c%s $secondLocation/$j.tif) -lt $min_size ]; then
#       yes=false
#       break
#     fi        
#   done

#   if [ $yes = true ]; then
#     echo "Found in second location: $range_start-$range_end"
#     ranges+=($range_start)
#   fi
# fi

# command should be like this:
# ffmpeg -start_number 1  -i /folder1/frame%04d.png
#        -start_number 31 -i /folder2/frame%04d.png
#        -start_number 61 -i /folder3/frame%04d.png
#        -filter_complex "concat=n=3" out.mp4

# but with these 2 exports
#
# ffmpeg -f image2 -framerate 24 -i ${out}/%04d.tif -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p /mnt/c/Users/trist/Desktop/outputDef.mp4
# ffmpeg -f image2 -framerate 24 -i ${out}/%04d.tif -c:v prores_ks -profile:v 3 /mnt/c/Users/trist/Desktop/outputProres.mov

# for every range started, switch to the second location at range_start
# for every range ended, switch back to the first location at range_end + 1
# but skip the last range if it ends at the last frame
cmd1="ffmpeg -f image2 -framerate 24 -start_number ${frame_start} -i ${out}/%04d.tif"
cmd2=" -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p /mnt/c/Users/trist/Desktop/outputDef.mp4"
cmd3=" -c:v prores_ks -profile:v 3 /mnt/c/Users/trist/Desktop/outputProres.mov"

for i in $(seq 0 $((${#ranges[@]} - 1))); do
  # Switch to secondLocation at the start of each range
  cmd1="$cmd1 -start_number ${ranges[$i]} -i ${secondLocation}/%04d.tif"
  
  # Switch back to out at the end of each range, unless it's the last range and it ends at the last frame
  if [ ${rangee[$i]} -ne $frame_end ]; then
    cmd1="$cmd1 -start_number $((${rangee[$i]} + 1)) -i ${out}/%04d.tif"
  fi
done

cmd="$cmd1 -filter_complex \"concat=n=$((${#ranges[@]} + 1))\" $cmd2"
echo $cmd
cmd="$cmd1 -filter_complex \"concat=n=$((${#ranges[@]} + 1))\" $cmd3"
echo $cmd