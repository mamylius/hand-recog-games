#!/bin/bash
# Start Python scripts in the background
python3 main_left.py & pids+=($!)
python3 main_left_2.py & pids+=($!)
python3 main_right.py & pids+=($!)
python3 main_right_2.py & pids+=($!)
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
