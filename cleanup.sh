#!/bin/bash

# Cleanup Script for CTF Lab Environment
# Removes monitoring stack and optionally k3s

set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

echo "========================================="
echo "K3s CTF Lab Environment - Cleanup"
echo "========================================="

# Set kubeconfig
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Ask for confirmation
read -p "This will remove the monitoring stack. Continue? (y/N): " -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Remove monitoring stack
if kubectl get namespace monitoring &> /dev/null; then
    echo "Removing monitoring stack..."
    kubectl delete namespace monitoring
    echo "✓ Monitoring stack removed"
else
    echo "Monitoring namespace not found, skipping..."
fi

# Ask about k3s removal
echo ""
read -p "Do you want to uninstall k3s as well? (y/N): " -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstalling k3s..."
    if command -v k3s-uninstall.sh &> /dev/null; then
        sudo /usr/local/bin/k3s-uninstall.sh
    else
        echo "Running k3s uninstall script..."
        sudo bash -c "$(curl -sfL https://get.k3s.io)" -- uninstall || true
    fi
    echo "✓ K3s uninstalled"
    
    # Clean up kubeconfig
    rm -f ~/.kube/config
    echo "✓ Kubeconfig removed"
else
    echo "K3s remains installed."
fi

echo ""
echo "========================================="
echo "Cleanup Complete!"
echo "========================================="
echo ""

