#!/bin/sh
set -e

GEOMETRY="${VNC_GEOMETRY:-1920x1080}"
DISPLAY="${DISPLAY:-:1}"
DISPLAY_NUM="${DISPLAY#:}"

echo "Preparing VNC session..."
echo "- Display:  ${DISPLAY}"
echo "- Geometry: ${GEOMETRY}"

# Clean up stale lock files from previous crashed sessions
rm -f "/tmp/.X${DISPLAY_NUM}-lock" "/tmp/.X11-unix/X${DISPLAY_NUM}"

# Clean up stale PID and log files
PID_FILE="$HOME/.vnc/$(hostname)${DISPLAY}.pid"
LOG_FILE="$HOME/.vnc/$(hostname)${DISPLAY}.log"
rm -f "$PID_FILE" "$LOG_FILE"

mkdir -p /tmp/.X11-unix

echo "Starting VNC server..."
vncserver "${DISPLAY}" -geometry "${GEOMETRY}"

echo "Waiting for VNC server to start..."

for i in $(seq 1 20); do
  if [ -f "$PID_FILE" ]; then
    VNC_PID=$(cat "$PID_FILE")
    if ps -p "$VNC_PID" >/dev/null 2>&1; then
      echo "VNC server started successfully (PID ${VNC_PID})."
      exit 0
    fi
  fi
  sleep 0.5
done

echo "Error: VNC server failed to start." >&2
[ -f "$LOG_FILE" ] && cat "$LOG_FILE" >&2
exit 1
