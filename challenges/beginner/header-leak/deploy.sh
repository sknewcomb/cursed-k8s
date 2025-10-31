#!/bin/bash
# Quick deployment script for the header-leak challenge

set -e

echo "Deploying Header Leak Challenge..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f configmap-app-code.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

echo ""
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/header-leak -n header-leak

echo ""
echo "Challenge deployed!"
echo ""
echo "Access the application:"
echo "  Web: http://localhost:30101"
echo "  Or: kubectl port-forward -n header-leak svc/header-leak 8080:8080"
echo ""
echo "Check pod status:"
echo "  kubectl get pods -n header-leak"

