#!/bin/sh
set -e

GEOMETRY="${VNC_GEOMETRY:-1920x1080}"
DISPLAY="${DISPLAY:-:1}"
DISPLAY_NUM="${DISPLAY#:}"
HOST="$(hostname)"

echo "Preparing VNC session..."
echo "  Display:  ${DISPLAY}"
echo "  Geometry: ${GEOMETRY}"

# Clean up stale lock files from previous crashed sessions
rm -f "/tmp/.X${DISPLAY_NUM}-lock" "/tmp/.X11-unix/X${DISPLAY_NUM}"

# Clean up stale PID and log files
rm -f "$HOME/.vnc/${HOST}${DISPLAY}.pid" "$HOME/.vnc/${HOST}${DISPLAY}.log"

mkdir -p /tmp/.X11-unix

echo "Starting VNC server..."
vncserver "${DISPLAY}" -geometry "${GEOMETRY}" -localhost no -fg &
VNC_PID=$!

echo "Waiting for VNC server to start..."

for i in $(seq 1 20); do
  if [ -f "$HOME/.vnc/${HOST}${DISPLAY}.pid" ] || ps -p "$VNC_PID" >/dev/null 2>&1; then
    echo "VNC server started successfully (PID ${VNC_PID})."
    exit 0
  fi
  sleep 0.5
done

echo "Error: VNC server failed to start." >&2
[ -f "$HOME/.vnc/${HOST}${DISPLAY}.log" ] && cat "$HOME/.vnc/${HOST}${DISPLAY}.log" >&2
exit 1
