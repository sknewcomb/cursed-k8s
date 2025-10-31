#!/bin/bash
# Quick deployment script for the file-disclosure challenge

set -e

echo "Deploying File Disclosure Challenge..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f configmap-app-code.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

echo ""
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/file-disclosure -n file-disclosure

echo ""
echo "Challenge deployed!"
echo ""
echo "Access the application:"
echo "  Web: http://localhost:30102"
echo "  Or: kubectl port-forward -n file-disclosure svc/file-disclosure 8080:8080"
echo ""
echo "Check pod status:"
echo "  kubectl get pods -n file-disclosure"

