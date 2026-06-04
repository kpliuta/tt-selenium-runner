#!/bin/sh
set -e

DISPLAY="${DISPLAY:-:1}"
DISPLAY_NUM="${DISPLAY#:}"
PID_FILE="$HOME/.vnc/$(hostname)${DISPLAY}.pid"

echo "Terminating VNC server on display ${DISPLAY}..."

# Try graceful shutdown via vncserver (reads PID file internally)
set +e
vncserver -kill "${DISPLAY}" >/dev/null 2>&1
set -e

# Wait a moment for graceful shutdown to take effect
sleep 1

# If the PID file still exists, force kill the process
if [ -f "$PID_FILE" ]; then
  VNC_PID=$(cat "$PID_FILE")
  kill -9 "$VNC_PID" 2>/dev/null || true
  rm -f "$PID_FILE"
fi

# Also find and kill any remaining Xtightvnc processes (handles the case
# where the PID file was lost but the server is still running)
set +e
pids=$(ps aux 2>/dev/null | grep '[X]tightvnc' | awk '{print $2}')
if [ -n "$pids" ]; then
  kill -9 $pids 2>/dev/null || true
fi
set -e

# Clean up lock files so start_vnc.sh gets a clean slate
rm -f "/tmp/.X${DISPLAY_NUM}-lock" "/tmp/.X11-unix/X${DISPLAY_NUM}"

echo "VNC server on display ${DISPLAY} terminated."
