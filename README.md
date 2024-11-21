# Nova Libvirt Exporter

A Prometheus exporter that provides detailed metrics from OpenStack Nova instances using libvirt. Monitor your virtual machines with comprehensive metrics about CPU, memory, network, disk, and PCI device information.

## Features

- Complete Nova instance metadata export
- Detailed CPU topology and usage metrics
- Memory allocation and balloon device tracking
- Network interface and IP configuration monitoring
- Storage and disk performance metrics
- PCI device mapping and passthrough monitoring
- Graphics and console configuration tracking
- System and OS information collection


## Quick Start

### Docker

```bash
docker run -d \
  --name nova-libvirt-exporter \
  -p 9179:9179 \
  -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \
  --privileged \
  sarabando/nova-libvirt-exporter
```

### Docker Compose

```yaml
version: '3'
services:
  exporter:
    image: sarabando/nova-libvirt-exporter
    ports:
      - "9179:9179"
    volumes:
      - /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock
    privileged: true
```

## Configuration

### Prometheus

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'nova-libvirt'
    static_configs:
      - targets: ['localhost:9179']
```

## Available Metrics

### Instance Metadata
- `nova_instance_metadata` - Basic instance information
- `nova_flavor_metadata` - Instance flavor details
- `nova_owner_metadata` - Instance ownership information

### System Metrics
- `nova_instance_memory_kib` - Memory allocation
- `nova_instance_vcpus` - vCPU allocation
- `nova_instance_cpu_shares` - CPU share allocation
- `nova_instance_cpu_topology` - CPU topology details

### Hardware Metrics
- `nova_instance_network` - Network interface configuration
- `nova_instance_disk` - Disk configuration
- `nova_instance_pci_device` - PCI device mapping
- `nova_instance_graphics` - Graphics configuration
- `nova_instance_memballoon` - Memory balloon device information

### Additional Information
- `nova_instance_sysinfo` - System information
- `nova_instance_os` - Operating system details
- `nova_instance_features` - Enabled features
- `nova_instance_console` - Console configuration

## Development

### Prerequisites
- Python 3.8+
- libvirt-dev
- pkg-config

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Run exporter
nova-libvirt-exporter
```

### Building

```bash
docker build -t sarabando/nova-libvirt-exporter .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
