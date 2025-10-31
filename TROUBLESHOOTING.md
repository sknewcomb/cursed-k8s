# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the k3s CTF lab environment.

## Common Issues

### Monitoring Stack Won't Start

#### Issue: Prometheus Pod Not Starting

**Symptoms:**
- Pod stays in `Pending` or `CrashLoopBackOff`
- `kubectl get pods -n monitoring` shows errors

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n monitoring -l app=prometheus

# Check pod logs
kubectl logs -n monitoring deployment/prometheus

# Check pod events
kubectl describe pod -n monitoring -l app=prometheus
```

**Common Causes:**
1. **ConfigMap not found**: Ensure ConfigMap exists
   ```bash
   kubectl get configmap -n monitoring prometheus-config
   ```
2. **Resource limits**: Check if node has enough resources
   ```bash
   kubectl top nodes
   ```
3. **Image pull issues**: Check if image can be pulled
   ```bash
   kubectl describe pod -n monitoring -l app=prometheus | grep -i image
   ```

**Fix:**
```bash
# Delete and redeploy
kubectl delete -f monitoring/prometheus/
kubectl apply -f monitoring/prometheus/
```

#### Issue: Grafana Pod Not Starting

**Symptoms:**
- Grafana pod crashes on startup
- Cannot access Grafana dashboard

**Diagnosis:**
```bash
# Check pod logs
kubectl logs -n monitoring deployment/grafana

# Check ConfigMap mounts
kubectl describe pod -n monitoring -l app=grafana | grep -A 10 "Mounts"
```

**Common Causes:**
1. **ConfigMap syntax error**: Invalid grafana.ini format
2. **Volume mount issues**: Check volume mounts in deployment
3. **Dashboard provisioning**: Dashboard ConfigMap not properly mounted

**Fix:**
```bash
# Verify all ConfigMaps exist
kubectl get configmap -n monitoring | grep grafana

# Ensure dashboard provisioning ConfigMap exists
kubectl apply -f monitoring/grafana/dashboard-provisioning.yaml

# Restart Grafana
kubectl rollout restart deployment/grafana -n monitoring
```

#### Issue: Status Page Not Starting

**Symptoms:**
- Status page pod stuck in `Init` or `CrashLoopBackOff`
- Takes very long to start

**Diagnosis:**
```bash
# Check pod logs (watch for pip install progress)
kubectl logs -n monitoring deployment/status-page -f

# Check if pip install is hanging
kubectl exec -n monitoring deployment/status-page -- ps aux
```

**Common Causes:**
1. **Slow pip install**: Installing packages on startup (first time only)
2. **Network issues**: Cannot reach PyPI
3. **Python dependencies**: Version conflicts

**Fix:**
- First startup takes 1-2 minutes for pip install - this is normal
- If it fails, check internet connectivity
- View logs to see specific error:
  ```bash
  kubectl logs -n monitoring deployment/status-page
  ```

### K3s Installation Issues

#### Issue: k3s Won't Start

**Symptoms:**
- `systemctl status k3s` shows failed
- `kubectl` commands fail

**Diagnosis:**
```bash
# Check k3s service status
sudo systemctl status k3s

# View detailed logs
sudo journalctl -u k3s -n 50

# Check for port conflicts
sudo netstat -tulpn | grep -E ':(6443|10250)'
```

**Common Causes:**
1. **Port conflicts**: Another service using k3s ports
2. **Disk space**: Not enough space for k3s
3. **Memory**: Insufficient RAM

**Fix:**
```bash
# Stop conflicting services
sudo systemctl stop <conflicting-service>

# Free up disk space
df -h

# Check available memory
free -h

# Reinstall k3s
sudo /usr/local/bin/k3s-uninstall.sh
sudo ./k3s-install.sh
```

#### Issue: Cannot Connect to Cluster

**Symptoms:**
- `kubectl get nodes` fails
- Connection refused errors

**Diagnosis:**
```bash
# Check kubeconfig
cat ~/.kube/config

# Verify k3s is running
sudo systemctl status k3s

# Test API server
curl -k https://localhost:6443
```

**Fix:**
```bash
# Set correct kubeconfig
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Or for regular user
export KUBECONFIG=~/.kube/config

# Verify connection
kubectl cluster-info
```

### Resource Issues

#### Issue: Out of Memory

**Symptoms:**
- Pods in `OOMKilled` state
- Cluster becomes unresponsive

**Diagnosis:**
```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -A

# Check system memory
free -h
```

**Fix:**
```bash
# Reduce resource requests in deployments
# Edit monitoring/*/deployment.yaml and reduce memory limits

# Scale down monitoring stack
kubectl scale deployment --replicas=0 -n monitoring prometheus
kubectl scale deployment --replicas=0 -n monitoring grafana
```

#### Issue: Out of Disk Space

**Symptoms:**
- Pods cannot start
- Image pull failures

**Diagnosis:**
```bash
# Check disk usage
df -h

# Check container storage
du -sh /var/lib/rancher/k3s/
```

**Fix:**
```bash
# Clean up unused images
kubectl get pods --all-namespaces
# Manually remove unused images via containerd

# Clean k3s data (careful!)
# This will delete all cluster data
sudo systemctl stop k3s
sudo rm -rf /var/lib/rancher/k3s/agent/containerd/io.containerd.content.v1.content/
```

### Network Issues

#### Issue: Cannot Access Services via NodePort

**Symptoms:**
- Cannot reach Grafana/Prometheus on NodePort
- Connection timeout

**Diagnosis:**
```bash
# Check service
kubectl get svc -n monitoring

# Check if NodePort is assigned
kubectl get svc -n monitoring grafana -o yaml | grep nodePort

# Test from inside cluster
kubectl run -it --rm test --image=curlimages/curl --restart=Never -- curl http://grafana.monitoring:3000
```

**Fix:**
```bash
# Use port-forward as workaround
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Check firewall rules
sudo iptables -L -n | grep 30300
sudo ufw status
```

#### Issue: Pods Cannot Reach Each Other

**Symptoms:**
- Grafana cannot connect to Prometheus
- DNS resolution failures

**Diagnosis:**
```bash
# Test DNS from pod
kubectl run -it --rm test --image=busybox --restart=Never -- nslookup prometheus.monitoring

# Check service endpoints
kubectl get endpoints -n monitoring
```

**Fix:**
```bash
# Verify services exist
kubectl get svc -n monitoring

# Restart CoreDNS if needed
kubectl rollout restart deployment/coredns -n kube-system
```

## Diagnostic Commands

### General Cluster Health
```bash
# Check all pods
kubectl get pods -A

# Check all services
kubectl get svc -A

# Check node status
kubectl get nodes

# Check events
kubectl get events -A --sort-by='.lastTimestamp' | tail -20
```

### Monitoring Stack Health
```bash
# Check all monitoring pods
kubectl get pods -n monitoring

# Check all monitoring services
kubectl get svc -n monitoring

# View Prometheus targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Then visit http://localhost:9090/targets

# Test Grafana health
kubectl exec -n monitoring deployment/grafana -- wget -qO- http://localhost:3000/api/health
```

### Resource Usage
```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -A

# Specific namespace
kubectl top pods -n monitoring
```

## Getting Help

If issues persist:

1. **Collect information:**
   ```bash
   kubectl get nodes -o wide
   kubectl get pods -A -o wide
   kubectl get svc -A
   kubectl get events -A
   ```

2. **Check logs:**
   ```bash
   # k3s logs
   sudo journalctl -u k3s -n 100
   
   # Pod logs
   kubectl logs -n monitoring deployment/prometheus
   kubectl logs -n monitoring deployment/grafana
   kubectl logs -n monitoring deployment/status-page
   ```

3. **Verify configuration:**
   ```bash
   # Check ConfigMaps
   kubectl get configmap -n monitoring -o yaml
   
   # Check RBAC
   kubectl get clusterrolebinding | grep -E "(prometheus|grafana|status-page)"
   ```

4. **Clean slate (last resort):**
   ```bash
   # Remove all monitoring resources
   kubectl delete namespace monitoring
   
   # Redeploy
   ./setup-monitoring.sh
   ```

