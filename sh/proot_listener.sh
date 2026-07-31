#!/bin/sh
# Runs INSIDE the proot-distro Ubuntu container.
# Listens to in.fifo for commands, executes them, and writes exit status to out.fifo.

in_fifo="/mnt/runner/in.fifo"
out_fifo="/mnt/runner/out.fifo"

# Wait for fifos to be created by the host process
while [ ! -p "$in_fifo" ] || [ ! -p "$out_fifo" ]; do
    sleep 0.1
done

while true; do
    if read -r cmd < "$in_fifo"; then
        if [ "$cmd" = "__shutdown__" ]; then
            # respond with success status end break the cmd loop immediately on shutdown
            echo "0" > "$out_fifo"
            break
        fi
        eval "$cmd"
        status=$?
        echo "$status" > "$out_fifo"
    fi
done
