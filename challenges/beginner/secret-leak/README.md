# Secret Leak Challenge

## Challenge Description

You've discovered a company's internal dashboard application running in their Kubernetes cluster. The application appears to be exposing sensitive information through various means. Your mission is to find the hidden flag!

**Difficulty:** Beginner  
**Category:** Configuration & Secret Management

## Learning Objectives

- Understand how ConfigMaps work in Kubernetes
- Learn why sensitive data should not be stored in ConfigMaps
- Practice using `kubectl` to inspect Kubernetes resources
- Identify common security misconfigurations

## Challenge Setup

The application is deployed in the `secret-leak` namespace. It's a simple web dashboard that exposes some API endpoints.

**Access the application:**
- Web Interface: `http://localhost:30100`
- Or use port-forward: `kubectl port-forward -n secret-leak svc/secret-leak 8080:8080`

## Your Mission

Find the flag hidden somewhere in this Kubernetes deployment. The flag format is: `FLAG{...}`

## Hints

1. ⚠️ ConfigMaps are not encrypted - anyone with `kubectl get configmap` access can read them
2. 🔍 Check the API endpoints exposed by the web application
3. 📋 Environment variables can expose more than expected
4. 🕵️ Use `kubectl` commands to inspect the deployment and its associated resources

## What to Look For

- Check what resources exist in the `secret-leak` namespace
- Examine the ConfigMaps for sensitive data
- Try accessing the API endpoints (`/api/info`, `/api/config`)
- Look at the deployment manifest for clues

## Getting Started

If you haven't deployed the challenge yet:

```bash
kubectl apply -f challenges/beginner/secret-leak/
```

## Verification

Once you find the flag, verify it matches the format `FLAG{...}`

## Solution Path

<details>
<summary>Click to reveal the solution path</summary>

1. Access the web application at `http://localhost:30100`
2. Try the `/api/config` endpoint which exposes all environment variables
3. Alternatively, use `kubectl get configmap secret-leak-config -n secret-leak -o yaml`
4. The flag is in the ConfigMap data as `FLAG`

</details>

## Security Lesson

This challenge demonstrates a common Kubernetes security mistake:
- **Never store secrets in ConfigMaps** - they are not encrypted and are readable by anyone with appropriate RBAC permissions
- Use Kubernetes Secrets for sensitive data (though even Secrets are base64 encoded, not encrypted by default)
- Consider using external secret management solutions for production environments
- Be careful about what environment variables your application exposes through API endpoints

