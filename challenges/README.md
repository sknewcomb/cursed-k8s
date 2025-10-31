# CTF Challenges

This directory is for organizing your CTF challenges and vulnerable applications.

## Directory Structure

Organize challenges by category or difficulty level:

```
challenges/
├── beginner/
├── intermediate/
├── advanced/
└── README.md
```

## Challenge Template

Each challenge should include:

1. **Challenge Description** (`README.md` or `CHALLENGE.md`)
   - Description of the vulnerability
   - Learning objectives
   - Hints (if any)

2. **Kubernetes Manifests** (`deployment.yaml`, `service.yaml`, etc.)
   - Deployment files for vulnerable applications
   - Services to expose the application
   - Any necessary ConfigMaps or Secrets

3. **Flag Location** (documented in challenge description)
   - Where students should find the flag
   - What the flag format is

## Example Challenge Structure

```
challenges/
└── example/
    ├── README.md
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml
```

## Deployment

Deploy a challenge using:

```bash
kubectl apply -f challenges/your-challenge/
```

## Best Practices

- Use namespaces to isolate challenges
- Document all flags and solutions separately (not in student-facing docs)
- Include hints that guide learning without giving away answers
- Test deployments before releasing to students
- Consider resource limits to prevent resource exhaustion

