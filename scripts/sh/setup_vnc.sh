#!/bin/sh
set -e

VNC_DIR="$HOME/.vnc"

if [ -f "$VNC_DIR/passwd" ]; then
    echo "VNC already configured, skipping setup."
    exit 0
fi

echo "Performing first-time VNC server setup..."

echo "  Creating directory: ${VNC_DIR}..."
mkdir -p "$VNC_DIR"

DEFAULT_PASS="termux"
echo "  Setting default VNC password to '${DEFAULT_PASS}'..."
echo "$DEFAULT_PASS" | vncpasswd -f > "$VNC_DIR/passwd"
chmod 600 "$VNC_DIR/passwd"

echo "  Creating xstartup file..."
cat << EOF > "$VNC_DIR/xstartup"
#!/bin/sh
startxfce4 &
EOF
chmod +x "$VNC_DIR/xstartup"

echo "VNC first-time setup complete (password: ${DEFAULT_PASS})."
