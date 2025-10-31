# Metrics Demo Application

A sample application that exposes Prometheus metrics for demonstration and testing purposes.

## What It Does

This application consists of:
- **Nginx web server**: Serves a simple web page
- **Nginx Prometheus Exporter**: Exports Nginx metrics in Prometheus format

## Metrics Exposed

The exporter exposes metrics like:
- `nginx_connections_active`: Active connections
- `nginx_connections_accepted`: Total accepted connections
- `nginx_connections_handled`: Total handled connections
- `nginx_http_requests_total`: Total HTTP requests
- `nginx_up`: Whether Nginx is up (1) or down (0)

## Access

**Web Interface:**
- http://localhost:30180

**Metrics Endpoint:**
- http://localhost:30113/metrics

## Deployment

```bash
kubectl apply -f examples/metrics-app/
```

## Viewing Metrics

### In Prometheus UI

1. Go to http://localhost:30090
2. Search for metrics starting with `nginx_`
3. Try queries like:
   ```promql
   nginx_connections_active
   rate(nginx_http_requests_total[5m])
   ```

### In Grafana

1. Go to http://localhost:30300
2. Create a new dashboard
3. Add panels with queries like:
   ```promql
   sum(rate(nginx_http_requests_total[5m])) by (instance)
   ```

## Testing

Generate some load to see metrics change:

```bash
# Generate requests
for i in {1..100}; do
  curl http://localhost:30180
  sleep 0.1
done
```

Then check the metrics in Prometheus to see the values change.

## Use Cases

- **Learning Prometheus**: Understand how metrics are exposed
- **Testing Alerts**: Trigger alerts by generating load
- **Dashboard Practice**: Create Grafana dashboards for these metrics
- **CTF Challenges**: Base for challenges involving metrics exposure

