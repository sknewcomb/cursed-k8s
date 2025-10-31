#!/bin/bash

# Deploy Example Applications Script
# Deploys example applications that expose Prometheus metrics

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Deploying Example Metrics Applications"
echo "========================================="

# Set kubeconfig
if [ -f /etc/rancher/k3s/k3s.yaml ]; then
    export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
elif [ -f ~/.kube/config ]; then
    export KUBECONFIG=~/.kube/config
fi

# Verify kubectl can connect
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster"
    echo "Please ensure k3s is running and kubeconfig is set correctly"
    exit 1
fi

# Deploy Nginx metrics app
echo ""
echo "Deploying Nginx Metrics Demo..."
if [ -d "examples/metrics-app" ]; then
    kubectl apply -f examples/metrics-app/
    echo "✓ Nginx metrics demo deployed"
    echo "  Web: http://localhost:30180"
    echo "  Metrics: http://localhost:30113/metrics"
else
    echo "⚠ examples/metrics-app/ not found, skipping..."
fi

# Deploy Python metrics app
echo ""
echo "Deploying Python Metrics Demo..."
if [ -d "examples/python-metrics-app" ]; then
    kubectl apply -f examples/python-metrics-app/
    echo "✓ Python metrics demo deployed"
    echo "  App: http://localhost:30181"
    echo "  Metrics: http://localhost:30181/metrics"
else
    echo "⚠ examples/python-metrics-app/ not found, skipping..."
fi

echo ""
echo "========================================="
echo "Example Applications Deployed!"
echo "========================================="
echo ""
echo "These applications expose Prometheus metrics that will be"
echo "automatically discovered by Prometheus service discovery."
echo ""
echo "Wait 30-60 seconds, then check Prometheus targets:"
echo "  http://localhost:30090/targets"
echo ""
echo "Or query metrics directly in Prometheus:"
echo "  http://localhost:30090"
echo ""
echo "Example queries:"
echo "  - nginx_connections_active"
echo "  - nginx_http_requests_total"
echo "  - http_requests_total"
echo "  - http_request_duration_seconds"
echo ""

