#!/bin/bash

# Exit immediately if a command exits with a non-zero status
echo "test"
set -e

echo "==> Updating package lists..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo "==> Installing prerequisites for Docker..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo "==> Adding Docker's official GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "==> Setting up the Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "==> Installing Docker Engine, Docker Compose, Python, Git, and Node.js..."
sudo apt-get update -y
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    python3 \
    python3-pip \
    git \
    nodejs \
    npm

echo "==> Configuring Docker permissions..."
sudo usermod -aG docker $USER"

echo "==> Install Java JDK..."
sudo apt install default-jdk

echo "==> Installation complete!"
echo "Note: Please log out and log back in (or restart your terminal) for the Docker group changes to take effect."