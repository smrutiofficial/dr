#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

PACKAGE_NAME="Dr_Linux"  # Replace with your package folder name.
DEB_FILE="$PACKAGE_NAME.deb"  # Replace with the name of your built .deb file.
SCRIPT_PATH="/bin/drlinux.py"  # Path to the script to run after installation.
VENV_DIR="/opt/drlinux_venv"  # Path to the virtual environment.
DESKTOP_FILE="/usr/share/applications/dr-linux.desktop"  # Path for the .desktop file.

# Step 1: Build the Debian package
echo "Building the Debian package..."
dpkg-deb --build "$PACKAGE_NAME"
echo "Build completed: $DEB_FILE"

# Step 2: Remove the previously installed package
if dpkg -l | grep -q "dr-linux"; then
    echo "Removing previously installed version..."
    sudo dpkg -r dr-linux
    sudo rm -rf /usr/share/applications/dr-linux.desktop
fi

# Step 3: Install the new Debian package
echo "Installing the new package..."
sudo dpkg -i "$DEB_FILE"

# Step 4: Check for missing dependencies and fix if necessary
echo "Checking and fixing missing dependencies..."
sudo apt-get install -f -y

# Step 5: Ensure the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    echo "Activating the virtual environment and installing dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install --upgrade customtkinter pillow cairosvg pystray
    deactivate
else
    echo "Virtual environment already exists at $VENV_DIR."
fi

# Step 6: Create the .desktop file
echo "Creating the .desktop file for Dr. Linux..."
sudo bash -c "cat > $DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Name=Dr.Linux
Comment=A GUI tool to manage Linux applications
StartupWMClass=dr.Linux
Exec=/opt/drlinux_venv/bin/python /bin/drlinux.py
Icon=/usr/share/icons/hicolor/256x256/apps/drlinux.png
Terminal=false
Type=Application
Categories=Utility;System;
EOF

# Ensure the .desktop file has the correct permissions
sudo chmod 644 "$DESKTOP_FILE"

# Step 7: Run the application using the virtual environment
echo "Running the application..."
if [ -f "$SCRIPT_PATH" ]; then
    echo "/opt/drlinux_venv/bin/python /bin/drlinux.py"
    "$VENV_DIR/bin/python" "$SCRIPT_PATH"
else
    echo "Error: Script not found at $SCRIPT_PATH."
    exit 1
fi
