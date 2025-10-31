# CTF Challenges Guide

This guide explains how to create, deploy, and manage CTF challenges in your k3s lab environment.

## Challenge Structure

### Recommended Directory Layout

```
challenges/
├── challenge-name/
│   ├── README.md              # Challenge description for students
│   ├── deployment.yaml        # Application deployment
│   ├── service.yaml           # Service exposure
│   ├── configmap.yaml        # Configuration (may contain hints/flags)
│   ├── secret.yaml           # Secrets (may contain flags)
│   └── solution.md           # Solution (keep private!)
```

## Creating a Challenge

### Step 1: Design the Vulnerability

Consider common Kubernetes security issues:
- **Misconfigured RBAC**: Overly permissive service accounts or roles
- **Exposed Secrets**: Secrets in ConfigMaps, environment variables
- **Privileged Containers**: Containers with host access
- **Network Policies**: Missing or incorrect network restrictions
- **Image Vulnerabilities**: Using vulnerable container images
- **API Exposure**: Exposed Kubernetes API endpoints

### Step 2: Create Kubernetes Manifests

#### Basic Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vulnerable-app
  namespace: challenge-ns
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vulnerable-app
  template:
    metadata:
      labels:
        app: vulnerable-app
    spec:
      serviceAccountName: vulnerable-sa  # Intentionally permissive
      containers:
      - name: app
        image: nginx:latest
        securityContext:
          privileged: true  # Vulnerability!
        env:
        - name: SECRET_KEY
          value: "CTF{flag_here}"  # Vulnerability!
```

#### Service Exposure

```yaml
apiVersion: v1
kind: Service
metadata:
  name: vulnerable-app
  namespace: challenge-ns
spec:
  type: NodePort
  ports:
  - port: 80
    nodePort: 30081
  selector:
    app: vulnerable-app
```

### Step 3: Write Challenge Documentation

Create a `README.md` for students:

```markdown
# Challenge: Vulnerable Web App

## Description
Find the hidden flag in this vulnerable application.

## Learning Objectives
- Understand Kubernetes pod security
- Learn about environment variable exposure
- Practice kubectl commands

## Hints
- Check the pod's environment variables
- Use `kubectl describe` to inspect resources

## Flag Format
CTF{...}
```

### Step 4: Create Solution Documentation

Create `solution.md` (keep this private!):

```markdown
# Solution: Vulnerable Web App

## Vulnerability
The deployment exposes sensitive data in environment variables.

## Solution Steps
1. Get the pod name: `kubectl get pods -n challenge-ns`
2. Describe the pod: `kubectl describe pod <pod-name> -n challenge-ns`
3. Find the SECRET_KEY environment variable
4. Extract the flag: CTF{flag_here}
```

## Deployment

### Deploy a Challenge

```bash
# Create namespace (if not in manifests)
kubectl create namespace challenge-ns

# Deploy challenge
kubectl apply -f challenges/challenge-name/

# Verify deployment
kubectl get pods -n challenge-ns
kubectl get svc -n challenge-ns
```

### Access the Challenge

```bash
# Get NodePort
kubectl get svc -n challenge-ns

# Or use port-forward
kubectl port-forward -n challenge-ns svc/vulnerable-app 8080:80
```

## Common Challenge Types

### 1. Secret Exposure

**Scenario**: Secrets stored in ConfigMap or environment variables

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  password: "CTF{flag_in_configmap}"
```

**Solution**: `kubectl get configmap app-config -o yaml`

### 2. Overly Permissive Service Account

**Scenario**: Service account with cluster-admin access

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: privileged-sa
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: privileged-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: privileged-sa
  namespace: default
```

**Solution**: Use the service account to access cluster resources

### 3. Privileged Container

**Scenario**: Container with host access

```yaml
securityContext:
  privileged: true
  capabilities:
    add:
    - SYS_ADMIN
  hostPID: true
```

**Solution**: Escape to host and find flag on filesystem

### 4. Exposed Debug Endpoint

**Scenario**: Application with debug endpoint exposing information

Deploy app with `/debug` endpoint returning pod information, secrets, etc.

**Solution**: Access the debug endpoint

### 5. Weak Image Security

**Scenario**: Using images with known vulnerabilities or backdoors

**Solution**: Analyze image, find backdoor, exploit it

## Testing Your Challenge

Before releasing to students:

1. **Deploy the challenge**
   ```bash
   kubectl apply -f challenges/your-challenge/
   ```

2. **Test the solution**
   - Try to solve it as a student would
   - Verify the flag is accessible
   - Ensure it's not too easy/hard

3. **Check resource usage**
   ```bash
   kubectl top pods -n challenge-ns
   ```

4. **Test cleanup**
   ```bash
   kubectl delete -f challenges/your-challenge/
   ```

## Challenge Best Practices

### 1. Isolation

- Use separate namespaces for each challenge
- Implement NetworkPolicies to isolate challenges
- Use resource limits to prevent resource exhaustion

### 2. Difficulty Levels

**Beginner:**
- Simple secret exposure
- Basic kubectl commands
- Clear hints

**Intermediate:**
- Multiple steps required
- RBAC exploitation
- Network policy bypass

**Advanced:**
- Container escape
- Cluster-wide privilege escalation
- Multi-stage attacks

### 3. Flag Placement

- Make flags meaningful (relate to the vulnerability)
- Use consistent flag format: `CTF{...}`
- Place flags where students learn something
- Don't make flags too obvious or too hidden

### 4. Documentation

- Clear challenge descriptions
- Learning objectives
- Appropriate hints (progressive if needed)
- Flag format specification

### 5. Resource Management

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

## Managing Challenges

### List All Challenges

```bash
ls challenges/
```

### Check Challenge Status

```bash
# List all challenge namespaces
kubectl get namespaces | grep challenge

# Check pods in a challenge
kubectl get pods -n challenge-ns
```

### Cleanup

```bash
# Remove a specific challenge
kubectl delete -f challenges/challenge-name/

# Remove all challenges
for dir in challenges/*/; do
    kubectl delete -f "$dir"
done
```

## Integration with Monitoring

Add Prometheus annotations to track challenge metrics:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

Create Grafana dashboards specific to challenges to track:
- Challenge access attempts
- Resource usage per challenge
- Student progress metrics

## Example Challenge: "The Leaky Pod"

See `examples/simple-webapp/` for a basic template.

A complete challenge example structure:

```
challenges/leaky-pod/
├── README.md
├── namespace.yaml
├── deployment.yaml
├── service.yaml
├── configmap.yaml
└── solution.md
```

## Troubleshooting

### Challenge Won't Deploy

```bash
# Check for errors
kubectl get events -n challenge-ns --sort-by='.lastTimestamp'

# Check pod status
kubectl describe pod <pod-name> -n challenge-ns
```

### Challenge Not Accessible

```bash
# Verify service exists
kubectl get svc -n challenge-ns

# Check NodePort is assigned
kubectl get svc -n challenge-ns -o yaml | grep nodePort

# Test connectivity
curl http://localhost:<nodePort>
```

### Resource Exhaustion

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -A

# Clean up unused challenges
kubectl delete namespace challenge-ns
```

## Security Considerations

⚠️ **Important**: These challenges contain intentional vulnerabilities!

1. **Isolation**: Run challenges in isolated namespaces
2. **Network**: Use firewall rules to limit access
3. **Resources**: Set resource limits on all challenges
4. **Monitoring**: Monitor for malicious activity
5. **Cleanup**: Regularly clean up completed challenges

## Resources

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [OWASP Kubernetes Security](https://owasp.org/www-project-kubernetes-top-ten/)
- [Kubernetes RBAC Guide](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

