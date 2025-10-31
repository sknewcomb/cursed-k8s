# Status Page

A lightweight web-based application status monitor for your k3s cluster. This status page provides a real-time dashboard showing the health and update status of all deployments and services in your cluster.

## Features

- **Real-time Monitoring**: Auto-refreshes every 30 seconds
- **Deployment Status**: View health, replicas, and update status of all deployments
- **Service Status**: Monitor service availability and endpoints
- **Update Tracking**: See which deployments are updating or up to date
- **Pod Details**: View individual pod status, restarts, and node assignment
- **Filtering**: Filter deployments by name or status
- **Beautiful UI**: Modern, responsive design with color-coded status indicators

## Access

After deployment, access the status page at:

**NodePort**: http://localhost:30088

Or use port-forwarding:
```bash
kubectl port-forward -n monitoring svc/status-page 8080:8080
# Then access: http://localhost:8080
```

## What It Shows

### Summary Cards
- Total deployments count
- Healthy deployments count
- Degraded deployments count
- Total services count

### Deployment Information
For each deployment, you can see:
- **Name and Namespace**: Deployment identification
- **Status**: Healthy, Degraded, or Unavailable
- **Update Status**: Up to date, Updating, or Update Failed
- **Replicas**: Ready vs Desired replica counts
- **Available Replicas**: Currently available pods
- **Container Images**: Images used by the deployment
- **Pod Details**: Individual pod status, restart counts, and node assignments

### Service Information
For each service, you can see:
- **Name and Namespace**: Service identification
- **Type**: ClusterIP, NodePort, LoadBalancer, etc.
- **Ports**: Exposed ports and protocols
- **Endpoints**: Number of backend endpoints
- **Cluster IP**: Internal cluster IP address
- **External IP**: If LoadBalancer type

## Status Indicators

### Deployment Status
- 🟢 **Healthy**: All replicas are ready and running
- 🟡 **Degraded**: Some replicas are not ready
- 🔴 **Unavailable**: No replicas are available

### Update Status
- 🔵 **Updating**: Deployment is currently rolling out an update
- 🟢 **Up to date**: Deployment is stable with no updates in progress

### Pod Status
- 🟢 **Running**: Pod is running successfully
- 🟡 **Pending**: Pod is waiting to start
- 🔴 **Failed**: Pod has failed to start

## Filtering

Use the search boxes and dropdowns to:
- Filter deployments by name
- Filter deployments by status (Healthy, Degraded, Unavailable)
- Filter services by name

## API Endpoint

The status page also exposes a REST API:

**GET /api/status**
Returns JSON with all deployment and service status information.

Example response:
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "deployments": [...],
  "services": [...],
  "summary": {
    "total_deployments": 5,
    "healthy_deployments": 4,
    "degraded_deployments": 1,
    "total_services": 8
  }
}
```

**GET /health**
Health check endpoint for monitoring.

## Architecture

The status page is a lightweight Python Flask application that:
1. Queries the Kubernetes API using the official Python client
2. Aggregates deployment and service information
3. Serves a single-page web application
4. Uses RBAC to read-only access to cluster resources

## Permissions

The status page uses a ServiceAccount with ClusterRole permissions to:
- List and get deployments
- List and get pods
- List and get services
- List and get endpoints

These are read-only permissions for security.

## Troubleshooting

### Status Page Not Loading

```bash
# Check if the pod is running
kubectl get pods -n monitoring -l app=status-page

# Check logs
kubectl logs -n monitoring deployment/status-page

# Check service
kubectl get svc -n monitoring status-page
```

### No Data Showing

```bash
# Verify RBAC permissions
kubectl get clusterrolebinding status-page
kubectl describe clusterrole status-page

# Check if the service account exists
kubectl get serviceaccount -n monitoring status-page
```

### API Errors

If you see "Error loading status" in the UI:
1. Check that the status page pod has proper RBAC permissions
2. Verify the service account is bound correctly
3. Check pod logs for specific error messages

## Customization

To customize the status page:
1. Modify the HTML template in `templates/index.html`
2. Adjust the Flask application logic in `app.py`
3. Rebuild and redeploy

## Auto-Refresh

The status page automatically refreshes every 30 seconds. You can also manually refresh by clicking the refresh button.

## Use Cases

- **CTF Lab Monitoring**: Quickly see which challenges are deployed and their status
- **Learning Tool**: Visualize Kubernetes deployments and services
- **Debugging**: Identify unhealthy deployments and pods
- **Update Tracking**: Monitor rolling updates in real-time

