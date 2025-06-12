#!/bin/bash
# Run the modprobe after reboot
# sudo modprobe v4l2loopback devices=4 video_nr=10,11,20,21 card_label="cam-vb,cam-vc,cam-vd,cam-ve"
# Map video devices
ffmpeg -f v4l2 -i /dev/video0   -map 0:v -f v4l2 /dev/video10   -map 0:v -f v4l2 /dev/video11 & pids+=($!)
ffmpeg -f v4l2 -i /dev/video2   -map 0:v -f v4l2 /dev/video20   -map 0:v -f v4l2 /dev/video21 & pids+=($!)

# Start Python scripts in the background
python main_multi.py --device /dev/video10 --half left --playerid 1 & pids+=($!)
python main_multi.py --device /dev/video11 --half right --playerid 2 & pids+=($!)
python main_multi.py --device /dev/video20 --half left --playerid 3 & pids+=($!)
python main_multi.py --device /dev/video21 --half right --playerid 4 & pids+=($!)
#python pong_increasing.py & pids+=($!)
echo "Started all scripts. Press [p] to stop them."
# Wait for 'p' keypress
while true; do
    read -rsn1 key
    if [[ "$key" == "p" ]]; then
        echo "Killing scripts..."
        for pid in "${pids[@]}"; do
            kill "$pid" 2>/dev/null
        done
        break
    fi
done
