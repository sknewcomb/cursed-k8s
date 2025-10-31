# K3s CTF Lab Environment

A lightweight Kubernetes (k3s) lab environment designed for CTF exercises, complete with monitoring dashboards and podman compatibility. Perfect for learning Kubernetes security and conducting Capture The Flag events.

## Features

- **Lightweight k3s Cluster**: Minimal resource footprint for lab environments
- **Monitoring Stack**: Prometheus + Grafana for cluster observability
- **Podman Compatible**: Works with Podman container runtime
- **CTF Ready**: Framework for deploying vulnerable applications and challenges
- **Easy Setup**: Automated deployment scripts and comprehensive documentation

## Quick Start

### Prerequisites

- Linux system (Ubuntu/Debian recommended)
- Root or sudo access
- Podman (optional, but recommended)
- At least 2GB RAM and 10GB disk space

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/cursed-k8s.git
   cd cursed-k8s
   ```

2. **Run the deployment script:**
   ```bash
   chmod +x *.sh
   sudo ./deploy.sh
   ```

3. **Access your services:**
   - Status Page: http://localhost:30088 (Application monitoring dashboard)
   - Grafana: http://localhost:30300 (admin/admin)
   - Prometheus: http://localhost:30090

### Verify Installation

```bash
# Set kubeconfig
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Check cluster status
kubectl get nodes
kubectl get pods -A
```

## Project Structure

```
cursed-k8s/
├── README.md                 # This file
├── deploy.sh                 # Main deployment script
├── setup-monitoring.sh       # Monitoring stack deployment
├── deploy-examples.sh        # Deploy example metrics applications
├── cleanup.sh                # Teardown script
├── k3s-install.sh           # K3s installation script
├── k3s-config.yaml          # K3s configuration template
├── monitoring/               # Monitoring stack manifests
│   ├── prometheus/
│   │   ├── alert-rules.yaml  # Prometheus alert rules
│   │   └── ...
│   └── grafana/
├── challenges/               # CTF challenges directory
├── examples/                 # Example vulnerable applications
└── docs/                     # Detailed documentation
    ├── INSTALL.md
    ├── MONITORING.md
    └── CHALLENGES.md
```

## Documentation

- [Installation Guide](docs/INSTALL.md) - Detailed installation instructions
- [Monitoring Guide](docs/MONITORING.md) - Using Prometheus and Grafana
- [Prometheus Uses](docs/PROMETHEUS_USES.md) - What you can do with Prometheus
- [Challenges Guide](docs/CHALLENGES.md) - Creating and deploying CTF challenges
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## Usage

### Deploying Challenges

1. Create your challenge manifests in `challenges/your-challenge/`
2. Deploy using kubectl:
   ```bash
   kubectl apply -f challenges/your-challenge/
   ```

### Deploying Example Metrics Applications

To deploy example applications that expose Prometheus metrics:

```bash
# Deploy all example apps
./deploy-examples.sh

# Or deploy individually
kubectl apply -f examples/metrics-app/
kubectl apply -f examples/python-metrics-app/
```

These applications will be automatically discovered by Prometheus service discovery.

### Monitoring Your Cluster

Access the Grafana dashboard at http://localhost:30300 to view:
- Cluster node status
- Pod resource usage (CPU, memory)
- Network I/O metrics
- Custom dashboards

### Managing the Environment

```bash
# View all services
kubectl get svc -A

# View pods
kubectl get pods -A

# Access a pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# View logs
kubectl logs <pod-name> -n <namespace>
```

## Podman Integration

This environment is designed to work with Podman. While k3s uses containerd by default, Podman can run containers in parallel. See [docs/INSTALL.md](docs/INSTALL.md) for Podman-specific setup instructions.

## Cleanup

To remove the monitoring stack and optionally k3s:

```bash
./cleanup.sh
```

## Security Considerations

⚠️ **Warning**: This environment is designed for lab/educational use. Do not deploy vulnerable applications or expose this environment to the internet without proper network isolation.

- Run in isolated networks or VMs
- Change default passwords (especially Grafana)
- Limit access to the Kubernetes API
- Use firewall rules to restrict access

## Troubleshooting

### K3s won't start
```bash
# Check k3s service status
sudo systemctl status k3s

# View logs
sudo journalctl -u k3s -f
```

### Cannot access Grafana/Prometheus
- Verify services are running: `kubectl get svc -n monitoring`
- Check NodePort values: `kubectl get svc -n monitoring -o yaml`
- Try port-forwarding: `kubectl port-forward -n monitoring svc/grafana 3000:3000`

### Pods in CrashLoopBackOff
```bash
# Check pod logs
kubectl logs <pod-name> -n <namespace>

# Describe pod for events
kubectl describe pod <pod-name> -n <namespace>
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Acknowledgments

- [k3s](https://k3s.io/) - Lightweight Kubernetes distribution
- [Prometheus](https://prometheus.io/) - Monitoring and alerting
- [Grafana](https://grafana.com/) - Visualization and dashboards

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review k3s documentation: https://k3s.io/

