#!/bin/bash

# Cleanup Script for CTF Lab Environment
# Removes monitoring stack, challenges, and optionally k3s
# Note: This script requires bash. Run with: ./cleanup.sh or bash cleanup.sh

# Check if running with bash (not sh)
if [ -z "${BASH_VERSION:-}" ]; then
    echo "Error: This script requires bash." >&2
    echo "Please run it with: ./cleanup.sh or bash cleanup.sh" >&2
    echo "Do not run with: sh cleanup.sh" >&2
    exit 1
fi

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "K3s CTF Lab Environment - Cleanup"
echo "========================================="

# Set kubeconfig
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# List of challenge namespaces to clean up
CHALLENGE_NAMESPACES="secret-leak header-leak file-disclosure hidden-params"

# Ask for confirmation
printf "This will remove the monitoring stack. Continue? (y/N): "
read -r REPLY
echo
if [ "$REPLY" != "y" ] && [ "$REPLY" != "Y" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Remove monitoring stack
if kubectl get namespace monitoring >/dev/null 2>&1; then
    echo "Removing monitoring stack..."
    kubectl delete namespace monitoring
    echo "✓ Monitoring stack removed"
else
    echo "Monitoring namespace not found, skipping..."
fi

# Ask about challenge cleanup
echo ""
printf "Do you want to remove all deployed challenges? (y/N): "
read -r REPLY
echo
if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
    echo "Removing challenges..."
    removed=0
    # shellcheck disable=SC2086
    for namespace in ${CHALLENGE_NAMESPACES}; do
        if kubectl get namespace "${namespace}" >/dev/null 2>&1; then
            echo "  Removing challenge: ${namespace}..."
            kubectl delete namespace "${namespace}" --wait=false || true
            removed=$((removed + 1))
        fi
    done
    
    if [ "${removed}" -gt 0 ]; then
        echo "✓ Removed ${removed} challenge namespace(s)"
        echo "  (Namespaces are being deleted in the background)"
    else
        echo "No challenge namespaces found, skipping..."
    fi
else
    echo "Challenges remain deployed."
fi

# Ask about k3s removal
echo ""
printf "Do you want to uninstall k3s as well? (y/N): "
read -r REPLY
echo
if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
    echo "Uninstalling k3s..."
    if command -v k3s-uninstall.sh >/dev/null 2>&1; then
        sudo /usr/local/bin/k3s-uninstall.sh
    else
        echo "Running k3s uninstall script..."
        # Use explicit bash -c with proper quoting
        uninstall_cmd='curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="uninstall" sh -'
        sudo bash -c "${uninstall_cmd}" || true
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

