# Nova Libvirt Exporter

A Prometheus exporter for OpenStack Nova instances using libvirt. This exporter provides detailed metrics about your Nova instances, including CPU, memory, network, disk, and PCI device information.

## Features

- Complete Nova instance metadata export
- CPU topology and configuration metrics
- Memory usage and balloon device metrics
- Network interface and IP address information
- Disk and storage metrics
- PCI device mapping and configuration
- Graphics and console configuration
- System and OS information

## Quick Start

### Using Docker

```bash
docker run -d \
  --name nova-libvirt-exporter \
  -p 9179:9179 \
  -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \
  --privileged \
  yourdockerhub/nova-libvirt-exporter
```

### Using Docker Compose

```bash
git clone https://github.com/yourusername/nova-libvirt-exporter
cd nova-libvirt-exporter
docker-compose up -d
```

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install the package:
```bash
pip install .
```

3. Run the exporter:
```bash
nova-libvirt-exporter
```

## Metrics

The exporter provides the following metrics:

- `nova_instance_metadata` - Basic instance information
- `nova_flavor_metadata` - Instance flavor details
- `nova_instance_cpu_topology` - CPU configuration
- `nova_instance_memory_kib` - Memory allocation
- `nova_instance_network` - Network interface details
- `nova_instance_pci_device` - PCI device mapping
- And many more...

## Configuration

### Prometheus Configuration

Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'nova-libvirt'
    static_configs:
      - targets: ['localhost:9179']
```

### Grafana Dashboard

A sample Grafana dashboard is provided in `examples/grafana-dashboard.json`.

## Development

### Building the Docker Image

```bash
docker build -t nova-libvirt-exporter .
```

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
