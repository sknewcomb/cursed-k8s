# Installation Guide

This guide provides detailed instructions for installing and configuring the k3s CTF lab environment.

## System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, or similar)
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 10GB free space
- **CPU**: 2 cores minimum
- **Network**: Internet connection for downloading images

### Recommended Requirements
- **RAM**: 4GB or more
- **Disk**: 20GB+ free space (SSD preferred)
- **CPU**: 4+ cores

## Prerequisites

### 1. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Tools

```bash
# Install curl (if not already installed)
sudo apt install -y curl wget

# Install kubectl (optional, k3s includes it)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### 3. Install Podman (Optional but Recommended)

```bash
# Ubuntu/Debian
sudo apt install -y podman

# Verify installation
podman --version
```

**Note**: While k3s uses containerd by default, Podman can run alongside for additional container management.

## Installation Methods

### Method 1: Automated Installation (Recommended)

The provided deployment script automates the entire process:

```bash
# Clone or download this repository
cd cursed-k8s

# Make scripts executable
chmod +x *.sh

# Run deployment script (requires sudo)
sudo ./deploy.sh
```

This script will:
1. Install k3s
2. Configure kubectl access
3. Deploy the monitoring stack (Prometheus + Grafana)
4. Display access information

### Method 2: Manual Installation

#### Step 1: Install k3s

```bash
# Install k3s with custom configuration
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode=644 --disable=traefik --disable=servicelb" sh -

# Verify installation
sudo systemctl status k3s
```

#### Step 2: Configure kubectl

```bash
# Set kubeconfig environment variable
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Or for non-root users
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
chmod 600 ~/.kube/config

# Update server URL
sed -i 's/127.0.0.1/localhost/g' ~/.kube/config
```

#### Step 3: Verify Cluster

```bash
kubectl get nodes
kubectl get pods -A
```

#### Step 4: Deploy Monitoring Stack

```bash
./setup-monitoring.sh
```

## Podman-Specific Configuration

### Running Podman with k3s

k3s uses containerd by default. Podman can run alongside k3s for additional container management:

1. **Check Podman socket** (if using rootless podman):
   ```bash
   podman system service --time 0 unix://$XDG_RUNTIME_DIR/podman/podman.sock
   ```

2. **Verify Podman is working**:
   ```bash
   podman run hello-world
   ```

3. **Note**: k3s containers will run via containerd, while your Podman containers run separately. This is normal and allows both to coexist.

### Podman Socket Setup

If you need k3s to use Podman (advanced):

1. Configure containerd to use Podman socket (requires containerd config modifications)
2. Or use k3s with containerd and run Podman separately (recommended)

## Configuration Options

### K3s Configuration File

For advanced configuration, create `/etc/rancher/k3s/config.yaml`:

```bash
sudo cp k3s-config.yaml /etc/rancher/k3s/config.yaml
# Edit the file as needed
sudo systemctl restart k3s
```

Common configuration options:
- **Disable Traefik**: Already disabled by default
- **Disable ServiceLB**: Already disabled by default
- **Custom CNI**: Modify CNI plugin
- **Resource Limits**: Adjust node resources

### Network Configuration

By default, k3s uses:
- **Cluster CIDR**: 10.42.0.0/16
- **Service CIDR**: 10.43.0.0/16

To modify these, edit `/etc/rancher/k3s/config.yaml`:

```yaml
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
```

## Post-Installation

### 1. Verify Installation

```bash
# Check k3s service
sudo systemctl status k3s

# Check nodes
kubectl get nodes

# Check all pods
kubectl get pods -A
```

### 2. Access Services

```bash
# Get service information
kubectl get svc -A

# Access Grafana (default: http://localhost:30300)
# Default credentials: admin/admin

# Access Prometheus (default: http://localhost:30090)
```

### 3. Test Deployment

Deploy a test application:

```bash
kubectl run test-pod --image=nginx --port=80
kubectl expose pod test-pod --port=80 --type=NodePort
kubectl get svc test-pod
```

## Troubleshooting

### K3s Installation Issues

**Issue**: k3s service fails to start

```bash
# Check logs
sudo journalctl -u k3s -n 50

# Common causes:
# - Port conflicts (6443, 10250, etc.)
# - Insufficient resources
# - Network issues
```

**Issue**: Cannot connect to cluster

```bash
# Verify kubeconfig
cat ~/.kube/config

# Check k3s is running
sudo systemctl status k3s

# Verify API server
curl -k https://localhost:6443
```

### Podman Issues

**Issue**: Podman containers not visible to k3s

This is expected. k3s uses containerd, Podman uses its own runtime. They operate independently.

**Issue**: Permission denied with Podman

```bash
# For rootless podman
podman unshare echo "test"

# Or use sudo podman
```

### Resource Issues

**Issue**: Out of memory

```bash
# Check system resources
free -h
df -h

# Adjust k3s resource limits in config.yaml
```

**Issue**: Disk space low

```bash
# Clean up unused images
kubectl get pods --all-namespaces
# Remove unused images manually or via cleanup script
```

## Uninstallation

To completely remove k3s:

```bash
# Use the cleanup script
./cleanup.sh

# Or manually
/usr/local/bin/k3s-uninstall.sh
```

## Next Steps

After installation:
1. Review the [Monitoring Guide](MONITORING.md) to set up dashboards
2. Read the [Challenges Guide](CHALLENGES.md) to deploy CTF challenges
3. Explore example applications in `examples/`

## Additional Resources

- [k3s Documentation](https://docs.k3s.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Podman Documentation](https://docs.podman.io/)

