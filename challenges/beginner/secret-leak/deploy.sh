#!/bin/bash
# Quick deployment script for the secret-leak challenge

set -e

echo "Deploying Secret Leak Challenge..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f configmap-app-code.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

echo ""
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/secret-leak -n secret-leak

echo ""
echo "Challenge deployed!"
echo ""
echo "Access the application:"
echo "  Web: http://localhost:30100"
echo "  Or: kubectl port-forward -n secret-leak svc/secret-leak 8080:8080"
echo ""
echo "Check pod status:"
echo "  kubectl get pods -n secret-leak"

