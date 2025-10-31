# Simple Web Application Example

A basic example web application template for CTF challenges.

## Deployment

```bash
kubectl apply -f examples/simple-webapp/
```

## Access

The service is exposed on NodePort 30080:

```bash
curl http://localhost:30080
```

Or use port-forwarding:

```bash
kubectl port-forward svc/simple-webapp 8080:80
curl http://localhost:8080
```

## Customization

This is a template. To create a challenge:

1. Modify the container image or add application code
2. Add vulnerabilities (e.g., exposed endpoints, weak authentication)
3. Add ConfigMaps or Secrets with sensitive data
4. Create misconfigurations (overly permissive service accounts, etc.)

## Example Vulnerabilities to Add

- Exposed `/debug` or `/admin` endpoints
- Default credentials in ConfigMap/Secret
- Environment variables with sensitive data
- Missing security contexts (privileged containers)
- Overly permissive service accounts
- Exposed internal APIs

