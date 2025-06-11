#!/bin/bash
# Start Python scripts in the background
python3 main_multi.py --device 0 --half left --playerid 1 & pids+=($!)
python3 main_multi.py --device 0 --half right --playerid 2 & pids+=($!)
python3 main_multi.py --device 1 --half left --playerid 3 & pids+=($!)
python3 main_multi.py --device 1 --half right --playerid 4 & pids+=($!)
python3 pong_increasing.py & pids+=($!)
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
