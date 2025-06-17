#!/usr/bin/env bash
set -euo pipefail
pids=()

# Load loopback with safe defaults
#sudo modprobe v4l2loopback devices=4 video_nr=10,11,20,21 card_label="cam-vb,cam-vc,cam-vd,cam-ve" flags=8 max_buffers=4

start_ffmpeg () {
  src="$1"; dst1="$2"; dst2="$3"
  ffmpeg -loglevel error -f v4l2 -input_format mjpeg -i "$src" \
         -map 0:v -f v4l2 "$dst1" \
         -map 0:v -f v4l2 "$dst2" &
  pids+=($!)
  until v4l2-ctl -d "$dst1" --all &>/dev/null; do sleep 0.2; done
}

start_ffmpeg /dev/video0 /dev/video10 /dev/video11
start_ffmpeg /dev/video2  /dev/video20 /dev/video21

python main_multi.py --device /dev/video10 --half left  --playerid 1 & pids+=($!)
python main_multi.py --device /dev/video11 --half right --playerid 2 & pids+=($!)
python main_multi.py --device /dev/video20 --half left  --playerid 3 & pids+=($!)
python main_multi.py --device /dev/video21 --half right --playerid 4 & pids+=($!)
python pong_increasing.py & pids+=($!)

trap 'echo "Cleaning up…"; for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null; done; exit' INT TERM
echo "Started. Press [p] to stop."

while IFS= read -rsn1 key; do
  [[ "$key" == "p" ]] && kill -TERM "$$"
done
