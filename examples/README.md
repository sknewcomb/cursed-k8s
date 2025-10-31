# Example Vulnerable Applications

This directory contains example vulnerable applications that can be used as starting points for CTF challenges.

## Purpose

These examples demonstrate common security misconfigurations and vulnerabilities in Kubernetes environments. Use them as templates or starting points for creating your own challenges.

## Example Applications

### Basic Web Application
A simple web application that can be configured with various security issues:
- Exposed sensitive endpoints
- Weak authentication
- Information disclosure

### Misconfigured Service
Services with common misconfigurations:
- Overly permissive service accounts
- Exposed internal services
- Missing network policies

### Container Escape
Examples demonstrating container escape scenarios:
- Privileged containers
- Host path mounts
- Capability abuse

## Usage

To deploy an example:

```bash
# Deploy the example
kubectl apply -f examples/example-name/

# Check the deployment
kubectl get pods -n example-namespace

# Access the service
kubectl port-forward -n example-namespace svc/example-service 8080:80
```

## Security Warning

These applications are intentionally vulnerable. **DO NOT** deploy them in production environments or on systems accessible from the internet without proper isolation.

## Contributing

When adding new examples:
1. Include a clear README explaining the vulnerability
2. Provide deployment manifests
3. Document the expected behavior and how to exploit it
4. Include remediation steps

