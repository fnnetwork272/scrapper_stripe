#!/bin/bash
set -e

# Create directory for Chrome and ChromeDriver
mkdir -p /opt/render/project/.render/chrome
cd /opt/render/project/.render/chrome

# Install dependencies using sudo apt-get
sudo apt-get update
sudo apt-get install -y wget unzip libnss3 libgconf-2-4 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4

# Download and install Google Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
ar x google-chrome-stable_current_amd64.deb
tar -xvf data.tar.xz
mv opt/google/chrome/* .
rm -rf data.tar.xz control.tar.gz debian-binary google-chrome-stable_current_amd64.deb opt

# Download and install ChromeDriver (use a specific version to avoid version mismatch)
CHROMEDRIVER_VERSION="126.0.6478.126"  # Adjust based on Chrome version if needed
wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

# Verify installations
if /opt/render/project/.render/chrome/google-chrome --version; then
    echo "Google Chrome installed successfully"
else
    echo "Google Chrome installation failed"
    exit 1
fi

if /usr/local/bin/chromedriver --version; then
    echo "ChromeDriver installed successfully"
else
    echo "ChromeDriver installation failed"
    exit 1
fi
