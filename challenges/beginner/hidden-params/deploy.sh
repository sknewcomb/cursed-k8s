#!/bin/bash
# Quick deployment script for the hidden-params challenge

set -e

echo "Deploying Hidden Params Challenge..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f configmap-app-code.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

echo ""
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/hidden-params -n hidden-params

echo ""
echo "Challenge deployed!"
echo ""
echo "Access the application:"
echo "  Web: http://localhost:30103"
echo "  Or: kubectl port-forward -n hidden-params svc/hidden-params 8080:8080"
echo ""
echo "Check pod status:"
echo "  kubectl get pods -n hidden-params"

