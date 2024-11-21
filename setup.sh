#!/bin/bash

# Step 1: Install required dependencies
echo "Installing necessary dependencies..."
sudo apt-get update
sudo apt-get install python3-pip -y
sudo apt-get install python3-pil -y
sudo apt-get install python3-numpy -y
sudo apt-get install python3-pandas -y
sudo apt-get install python3-smbus -y
sudo apt-get install -y tmux python3-pip

# Step 2: Set up the autostart script
echo "Setting up autostart..."

# 2.1: Create the autostart directory if it doesn't exist
AUTOSTART_DIR="/home/$(whoami)/.config/autostart"
mkdir -p $AUTOSTART_DIR

# 2.2: Create the autostart.sh script if it doesn't exist
AUTOSTART_SH="/home/$(whoami)/autostart.sh"
cat << EOF > $AUTOSTART_SH
#!/bin/bash

# Get the current username
USERNAME=$(whoami)

# Construct the path dynamically
APP_PATH="/home/\$USERNAME/Pandas-Digital-Scale/src/app.py"

# Run the Python application with the device as an argument
python3 \$APP_PATH
EOF

# Make autostart.sh executable
chmod +x $AUTOSTART_SH

# Step 4: Create the autostart desktop entry
DESKTOP_FILE="$AUTOSTART_DIR/pandas-digital-scale.desktop"
cat << EOF > $DESKTOP_FILE
[Desktop Entry]
Type=Application
Name=Pandas Digital Scale
Exec=tmux new-session -d -s startup "/home/$(whoami)/autostart.sh"; tmux attach-session -t startup
StartupNotify=true
NoDisplay=false
EOF

# Step 5: Notify the user
echo "Autostart setup complete. The app will run on startup."
echo "To test immediately, run 'xterm -e /home/$(whoami)/autostart.sh'."

echo "Setup complete!"
