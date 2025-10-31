#!/bin/bash

# Main Deployment Script for CTF Lab Environment
# This script deploys k3s and the monitoring stack

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "K3s CTF Lab Environment - Deployment"
echo "========================================="

# Check if k3s is installed
if ! command -v k3s &> /dev/null; then
    echo "K3s not found. Installing k3s..."
    sudo bash "$SCRIPT_DIR/k3s-install.sh"
else
    echo "✓ K3s is already installed"
fi

# Wait for k3s to be ready
echo "Checking k3s cluster status..."
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Retry loop for k3s readiness
MAX_RETRIES=30
RETRY_COUNT=0
while ! kubectl get nodes &> /dev/null; do
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "✗ Timeout waiting for k3s to be ready"
        exit 1
    fi
    echo "Waiting for k3s to be ready... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

echo "✓ K3s cluster is ready"

# Deploy monitoring stack
echo ""
echo "Deploying monitoring stack..."
bash "$SCRIPT_DIR/setup-monitoring.sh"

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Access your services:"
echo ""
kubectl get svc -A | grep -E "(prometheus|grafana|status-page)" | awk '{print "  " $1 "/" $2 " - " $4}'
echo ""
echo "Service URLs:"
echo "  Status Page: http://localhost:30088 (Application monitoring dashboard)"
echo "  Grafana: http://localhost:30300 (admin / admin - change on first login)"
echo "  Prometheus: http://localhost:30090 (with alert rules configured)"
echo ""
echo "Monitoring Features Installed:"
echo "  ✓ Prometheus with alerting rules"
echo "  ✓ Grafana dashboards"
echo "  ✓ Status page for application monitoring"
echo ""
echo "Optional: Deploy example metrics applications:"
echo "  kubectl apply -f examples/metrics-app/"
echo "  kubectl apply -f examples/python-metrics-app/"
echo ""
echo "View all services: kubectl get svc -A"
echo ""
echo "Documentation:"
echo "  - Prometheus uses: docs/PROMETHEUS_USES.md"
echo "  - Monitoring guide: docs/MONITORING.md"
echo ""

