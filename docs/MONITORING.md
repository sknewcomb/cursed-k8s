# Monitoring Guide

This guide explains how to use Prometheus and Grafana to monitor your k3s CTF lab environment.

## Overview

The monitoring stack includes:
- **Status Page**: Real-time application status dashboard
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards

All services are deployed in the `monitoring` namespace and exposed via NodePort.

## Accessing Services

### Status Page

**Default Access:**
- URL: http://localhost:30088

**Alternative Access (Port Forward):**
```bash
kubectl port-forward -n monitoring svc/status-page 8080:8080
# Access at http://localhost:8080
```

The status page provides:
- Real-time deployment and service status
- Update/rollout monitoring
- Pod health and restart information
- Filtering and search capabilities

See [Status Page README](../status-page/README.md) for detailed information.

### Grafana Dashboard

**Default Access:**
- URL: http://localhost:30300
- Username: `admin`
- Password: `admin`

**Important**: Change the default password on first login!

**Alternative Access (Port Forward):**
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Access at http://localhost:3000
```

### Prometheus UI

**Default Access:**
- URL: http://localhost:30090

**Alternative Access (Port Forward):**
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Access at http://localhost:9090
```

## Grafana Dashboards

### Default Dashboard

After logging in, you'll see the "K3s Cluster Overview" dashboard with:
- CPU usage per pod
- Memory usage per pod
- Pod status table
- Node status
- Running pods count
- Network I/O metrics

### Viewing Dashboards

1. Login to Grafana
2. Navigate to **Dashboards** (left menu)
3. Select **K3s Cluster Overview**

### Creating Custom Dashboards

1. Click **+** → **Create Dashboard**
2. Add panels with Prometheus queries
3. Example queries:
   ```promql
   # CPU usage
   rate(container_cpu_usage_seconds_total[5m])
   
   # Memory usage
   container_memory_usage_bytes
   
   # Pod count
   count(kube_pod_info)
   ```

## Prometheus Queries

### Basic Metrics

**Node Information:**
```promql
kube_node_info
```

**Pod Status:**
```promql
kube_pod_status_phase
```

**CPU Usage:**
```promql
rate(container_cpu_usage_seconds_total[5m])
```

**Memory Usage:**
```promql
container_memory_usage_bytes
```

**Network Traffic:**
```promql
rate(container_network_receive_bytes_total[5m])
rate(container_network_transmit_bytes_total[5m])
```

### Useful Queries

**Running Pods Count:**
```promql
count(kube_pod_status_phase{phase="Running"})
```

**Pod Restarts:**
```promql
kube_pod_container_status_restarts_total
```

**Resource Requests vs Limits:**
```promql
kube_pod_container_resource_requests
kube_pod_container_resource_limits
```

## Monitoring CTF Challenges

### Adding Challenge Metrics

To monitor your CTF challenges, ensure pods have Prometheus annotations:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

### Creating Challenge-Specific Dashboards

1. Identify metrics your challenge exposes
2. Create a Grafana dashboard
3. Add panels for challenge-specific metrics
4. Share dashboard JSON or export it

## Alerting (Optional)

### Setting Up Alerts in Grafana

1. Navigate to **Alerting** → **Alert rules**
2. Click **Create alert rule**
3. Define conditions (e.g., CPU > 80%)
4. Configure notification channels

### Example Alert Rules

**High CPU Usage:**
```
WHEN avg() OF query(A, 5m, now) IS ABOVE 80
```

**Pod Crash:**
```
WHEN sum() OF kube_pod_container_status_restarts_total IS ABOVE 5
```

## Scrape Configuration

Prometheus automatically scrapes:
- Kubernetes API server
- Kubernetes nodes (via kubelet)
- Pods with `prometheus.io/scrape` annotation
- Services with `prometheus.io/probe` annotation

### Viewing Scrape Targets

In Prometheus UI:
1. Go to **Status** → **Targets**
2. View all configured scrape targets
3. Check their health status

### Adding Custom Scrape Targets

Edit `monitoring/prometheus/configmap.yaml` and add to `scrape_configs`:

```yaml
- job_name: 'my-service'
  static_configs:
    - targets: ['my-service:8080']
```

Then apply changes:
```bash
kubectl apply -f monitoring/prometheus/configmap.yaml
kubectl rollout restart deployment/prometheus -n monitoring
```

## Troubleshooting

### Grafana Not Loading

```bash
# Check pod status
kubectl get pods -n monitoring

# Check logs
kubectl logs -n monitoring deployment/grafana

# Check service
kubectl get svc -n monitoring grafana
```

### Prometheus Not Scraping

```bash
# Check Prometheus configuration
kubectl get configmap -n monitoring prometheus-config -o yaml

# Check targets in Prometheus UI
# Go to Status → Targets

# View Prometheus logs
kubectl logs -n monitoring deployment/prometheus
```

### Missing Metrics

1. Verify pods have Prometheus annotations
2. Check if metrics endpoint is accessible:
   ```bash
   kubectl exec -it <pod-name> -n <namespace> -- wget -qO- http://localhost:8080/metrics
   ```
3. Check Prometheus scrape configuration

### Dashboard Not Displaying Data

1. Verify Prometheus datasource in Grafana:
   - Go to **Configuration** → **Data sources**
   - Test connection to Prometheus
2. Check time range in dashboard
3. Verify queries return data in Prometheus UI

## Advanced Configuration

### Persistent Storage for Grafana

To persist Grafana dashboards across restarts, modify `monitoring/grafana/deployment.yaml`:

```yaml
volumes:
- name: grafana-storage
  persistentVolumeClaim:
    claimName: grafana-pvc
```

Create PVC:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### Retention Period

Adjust Prometheus retention in `monitoring/prometheus/deployment.yaml`:

```yaml
args:
  - '--storage.tsdb.retention.time=30d'  # Change from 7d to 30d
```

## Best Practices

1. **Change Default Passwords**: Update Grafana admin password immediately
2. **Limit Access**: Use firewall rules to restrict access to monitoring services
3. **Monitor Resources**: Watch resource usage to prevent cluster exhaustion
4. **Regular Backups**: Export important Grafana dashboards as JSON
5. **Label Metrics**: Use consistent labels for better querying
6. **Set Alerts**: Configure alerts for critical metrics

## Resources

- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Kubernetes Metrics](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)

