# What Can You Use Prometheus For?

Prometheus is a powerful monitoring and alerting toolkit. Here's what you can do with it in your k3s CTF lab environment.

## Core Capabilities

### 1. **Metrics Collection**
Prometheus scrapes metrics from various sources:
- **Kubernetes components**: API server, nodes, pods
- **Applications**: Any service that exposes a `/metrics` endpoint
- **System resources**: CPU, memory, disk, network
- **Custom metrics**: Business logic, application-specific data

### 2. **Time-Series Database**
- Stores metrics with timestamps
- Efficient querying with PromQL (Prometheus Query Language)
- Built-in retention policies (7 days by default)
- Handles millions of time series

### 3. **Querying & Analysis**
Query metrics using PromQL to:
- Calculate rates, averages, percentiles
- Compare current vs historical values
- Aggregate across multiple metrics
- Filter and group by labels

### 4. **Alerting**
Define rules that trigger when conditions are met:
- High CPU/memory usage
- Service downtime
- Error rate thresholds
- Custom business logic

## Real-World Use Cases

### Infrastructure Monitoring

**Node Health:**
```promql
# Node CPU usage
100 - (avg by (instance) (rate(container_cpu_usage_seconds_total[5m])) * 100)

# Node memory usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```

**Pod Monitoring:**
```promql
# Pod restarts
rate(kube_pod_container_status_restarts_total[5m])

# Pod resource usage
container_memory_usage_bytes{container_name!="POD"}
```

### Application Monitoring

**HTTP Metrics:**
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Request latency (99th percentile)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

**Service Availability:**
```promql
# Uptime percentage
avg_over_time(up[1h]) * 100
```

### Capacity Planning

**Resource Trends:**
```promql
# Memory growth over time
predict_linear(container_memory_usage_bytes[1h], 3600)

# Disk space prediction
predict_linear(node_filesystem_avail_bytes[6h], 86400)
```

### Security Monitoring

**Anomaly Detection:**
```promql
# Unusual request patterns
rate(http_requests_total[5m]) > 1000

# Failed authentication attempts
rate(login_failures_total[5m]) > 10
```

## What's Included in This Lab

### Pre-Configured Monitoring

1. **Kubernetes Components:**
   - API server metrics
   - Node metrics (CPU, memory, disk)
   - Pod metrics (resource usage, restarts)
   - Service discovery for all pods

2. **Alert Rules:**
   - High CPU/memory usage
   - Pod crash loops
   - Node availability
   - Service downtime
   - Resource exhaustion

3. **Example Applications:**
   - Nginx metrics exporter (exposes connection/request metrics)
   - Python metrics demo (custom application metrics)

### Ready-to-Use Metrics

**System Metrics:**
- `container_cpu_usage_seconds_total`: CPU usage per container
- `container_memory_usage_bytes`: Memory usage per container
- `container_network_receive_bytes_total`: Network ingress
- `container_network_transmit_bytes_total`: Network egress

**Kubernetes Metrics:**
- `kube_pod_status_phase`: Pod lifecycle status
- `kube_node_status_condition`: Node health
- `kube_pod_container_status_restarts_total`: Restart counts

**Application Metrics (from demo apps):**
- `nginx_connections_active`: Active Nginx connections
- `nginx_http_requests_total`: HTTP request count
- `http_requests_total`: Custom HTTP metrics
- `http_request_duration_seconds`: Request latency

## Common Prometheus Queries

### Resource Usage

```promql
# Top 10 pods by CPU
topk(10, sum by (pod_name) (rate(container_cpu_usage_seconds_total[5m])))

# Memory usage percentage
(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100
```

### Availability

```promql
# Service uptime
avg_over_time(up[24h]) * 100

# Failed pods
count(kube_pod_status_phase{phase!="Running"})
```

### Performance

```promql
# Average request duration
avg(rate(http_request_duration_seconds_sum[5m])) / avg(rate(http_request_duration_seconds_count[5m]))

# Requests per second
sum(rate(http_requests_total[1m]))
```

## CTF Challenge Ideas

### 1. **Metrics Analysis Challenge**
- Expose sensitive information in metrics
- Students must query Prometheus to find flags
- Example: API keys in metric labels or values

### 2. **Alert Exploitation**
- Misconfigured alerts expose internal endpoints
- Alert webhook URLs contain sensitive data
- Students trigger alerts to gain access

### 3. **Metrics Endpoint Security**
- Exposed `/metrics` endpoints with sensitive data
- Students exploit unauthenticated metrics access
- Use metrics to discover internal architecture

### 4. **Performance DoS**
- Create alerts that consume resources
- Query expensive metrics to exhaust Prometheus
- Exploit query complexity

## Best Practices

1. **Label Everything**: Use consistent, meaningful labels
2. **Cardinality Management**: Avoid high-cardinality labels (user IDs, etc.)
3. **Query Optimization**: Use recording rules for expensive queries
4. **Alert Tuning**: Set appropriate thresholds and durations
5. **Retention**: Balance storage costs vs historical data needs

## Next Steps

1. **Explore Pre-Built Dashboards**: Check Grafana for example dashboards
2. **Deploy Example Apps**: `kubectl apply -f examples/metrics-app/`
3. **Create Custom Metrics**: Add Prometheus client to your applications
4. **Write Your Own Queries**: Experiment in Prometheus UI
5. **Set Up Alerts**: Modify alert rules in `monitoring/prometheus/alert-rules.yaml`

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Kubernetes Metrics](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)

