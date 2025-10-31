#!/bin/bash

# Monitoring Stack Deployment Script
# Deploys Prometheus and Grafana for k3s cluster monitoring

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Deploying Monitoring Stack"
echo "========================================="

# Set kubeconfig - try multiple locations
if [ -f /etc/rancher/k3s/k3s.yaml ]; then
    export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
elif [ -f ~/.kube/config ]; then
    export KUBECONFIG=~/.kube/config
else
    echo "Warning: kubeconfig not found. Trying to use default..."
fi

# Verify kubectl can connect
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster"
    echo "Please ensure k3s is running and kubeconfig is set correctly"
    exit 1
fi

# Create monitoring namespace
echo "Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Deploy Prometheus
echo ""
echo "Deploying Prometheus..."
kubectl apply -f monitoring/prometheus/
echo "Deploying Prometheus alert rules..."
kubectl apply -f monitoring/prometheus/alert-rules.yaml

# Wait for Prometheus ConfigMaps to be ready
echo "Waiting for Prometheus ConfigMaps..."
kubectl wait --for=condition=ready --timeout=30s configmap/prometheus-config -n monitoring 2>/dev/null || true
kubectl wait --for=condition=ready --timeout=30s configmap/prometheus-alert-rules -n monitoring 2>/dev/null || true

# Wait for Prometheus to be ready
echo "Waiting for Prometheus deployment..."
kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n monitoring 2>/dev/null || {
    echo "Warning: Prometheus deployment not ready. Check with: kubectl get pods -n monitoring"
    kubectl get pods -n monitoring -l app=prometheus
}

# Deploy Grafana
echo ""
echo "Deploying Grafana..."
kubectl apply -f monitoring/grafana/
kubectl apply -f monitoring/grafana/dashboard-provisioning.yaml

# Wait for Grafana ConfigMaps to be ready
echo "Waiting for Grafana ConfigMaps..."
kubectl wait --for=condition=ready --timeout=30s configmap/grafana-config -n monitoring 2>/dev/null || true
kubectl wait --for=condition=ready --timeout=30s configmap/grafana-datasource -n monitoring 2>/dev/null || true

# Wait for Grafana to be ready
echo "Waiting for Grafana deployment..."
kubectl wait --for=condition=available --timeout=300s deployment/grafana -n monitoring 2>/dev/null || {
    echo "Warning: Grafana deployment not ready. Check with: kubectl get pods -n monitoring"
    kubectl get pods -n monitoring -l app=grafana
}

# Deploy Status Page
echo ""
echo "Deploying Status Page..."
kubectl apply -f status-page/configmap-app.yaml
kubectl apply -f status-page/configmap-template.yaml
kubectl apply -f status-page/deployment.yaml

# Wait for Status Page to be ready (give it time to install dependencies)
echo "Waiting for Status Page to be ready (this may take 1-2 minutes for initial pip install)..."
kubectl wait --for=condition=available --timeout=600s deployment/status-page -n monitoring 2>/dev/null || {
    echo "Warning: Status Page deployment not ready. It may still be installing Python packages."
    echo "Check with: kubectl logs -n monitoring deployment/status-page"
    kubectl get pods -n monitoring -l app=status-page
}

# Display service information
echo ""
echo "========================================="
echo "Monitoring Stack Deployed!"
echo "========================================="
echo ""
echo "Services:"
kubectl get svc -n monitoring
echo ""
echo "Access Grafana:"
GRAFANA_PORT=$(kubectl get svc grafana -n monitoring -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}')
if [ -n "$GRAFANA_PORT" ]; then
    echo "  http://localhost:$GRAFANA_PORT"
    echo "  Default credentials: admin / admin"
else
    echo "  Run: kubectl port-forward -n monitoring svc/grafana 3000:3000"
    echo "  Then access: http://localhost:3000"
fi
echo ""
echo "Access Prometheus:"
PROMETHEUS_PORT=$(kubectl get svc prometheus -n monitoring -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}')
if [ -n "$PROMETHEUS_PORT" ]; then
    echo "  http://localhost:$PROMETHEUS_PORT"
else
    echo "  Run: kubectl port-forward -n monitoring svc/prometheus 9090:9090"
    echo "  Then access: http://localhost:9090"
fi
echo ""
echo "Access Status Page:"
STATUS_PAGE_PORT=$(kubectl get svc status-page -n monitoring -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}')
if [ -n "$STATUS_PAGE_PORT" ]; then
    echo "  http://localhost:$STATUS_PAGE_PORT"
else
    echo "  Run: kubectl port-forward -n monitoring svc/status-page 8080:8080"
    echo "  Then access: http://localhost:8080"
fi
echo ""
echo "========================================="
echo "Next Steps"
echo "========================================="
echo ""
PROMETHEUS_PORT=$(kubectl get svc prometheus -n monitoring -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}' 2>/dev/null || echo "30090")
echo "Prometheus Features:"
echo "  ✓ Alert rules deployed - View alerts at: http://localhost:${PROMETHEUS_PORT}/alerts"
echo "  ✓ Kubernetes metrics scraping enabled"
echo "  ✓ Service discovery configured"
echo ""
echo "To deploy example metrics applications:"
echo "  kubectl apply -f examples/metrics-app/"
echo "  kubectl apply -f examples/python-metrics-app/"
echo ""
echo "These apps expose Prometheus metrics that will be automatically discovered."
echo "See examples/metrics-app/README.md and docs/PROMETHEUS_USES.md for details."
echo ""

