#!/bin/bash

# K3s Installation Script for CTF Lab Environment
# This script installs k3s with podman compatibility

set -e

echo "========================================="
echo "K3s CTF Lab Environment - Installation"
echo "========================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Check for podman
if ! command -v podman &> /dev/null; then
    echo "Warning: podman not found. K3s will use containerd by default."
    echo "You may need to configure k3s to use podman socket."
fi

echo "Installing k3s..."

# Install k3s with specific flags for lab environment
export INSTALL_K3S_EXEC="--write-kubeconfig-mode=644 --disable=traefik --disable=servicelb"

# Download and install k3s
curl -sfL https://get.k3s.io | sh -

# Configure k3s to work with podman if podman is available
if command -v podman &> /dev/null; then
    echo "Configuring k3s for podman compatibility..."
    
    # Check if podman socket exists
    if [ -S "/run/podman/podman.sock" ]; then
        echo "Podman socket found at /run/podman/podman.sock"
        # Note: k3s uses containerd by default, but we can configure the node to use podman if needed
        echo "Note: k3s uses containerd by default. Podman containers will run separately."
    fi
fi

# Wait for k3s to be ready
echo "Waiting for k3s to be ready..."
sleep 5

# Check k3s status
echo "Checking k3s service status..."
if systemctl is-active --quiet k3s; then
    echo "✓ k3s service is running"
else
    echo "✗ k3s failed to start. Check logs with: sudo journalctl -u k3s"
    exit 1
fi

# Wait a bit more and verify kubectl works
sleep 3
if kubectl get nodes &> /dev/null; then
    echo "✓ k3s cluster is ready and accessible"
else
    echo "⚠ Warning: k3s is running but kubectl cannot connect yet."
    echo "  This may be normal during startup. Wait a few seconds and try:"
    echo "  kubectl get nodes"
fi

# Set up kubeconfig for non-root user (if not root)
if [ -n "$SUDO_USER" ]; then
    echo "Setting up kubeconfig for user: $SUDO_USER"
    mkdir -p /home/$SUDO_USER/.kube
    cp /etc/rancher/k3s/k3s.yaml /home/$SUDO_USER/.kube/config
    chown $SUDO_USER:$SUDO_USER /home/$SUDO_USER/.kube/config
    chmod 600 /home/$SUDO_USER/.kube/config
    
    # Update server URL to localhost
    sed -i 's/127.0.0.1/localhost/g' /home/$SUDO_USER/.kube/config
fi

# Copy kubeconfig to root
mkdir -p /root/.kube
cp /etc/rancher/k3s/k3s.yaml /root/.kube/config
sed -i 's/127.0.0.1/localhost/g' /root/.kube/config

echo ""
echo "========================================="
echo "K3s Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Verify installation: kubectl get nodes"
echo "2. Deploy monitoring stack: ./setup-monitoring.sh"
echo "3. Or run full deployment: ./deploy.sh"
echo ""
echo "To use kubectl, you may need to:"
echo "  export KUBECONFIG=/etc/rancher/k3s/k3s.yaml"
echo "  # or for regular user:"
echo "  export KUBECONFIG=~/.kube/config"
echo ""

