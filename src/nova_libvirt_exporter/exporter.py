import libvirt
import xml.etree.ElementTree as ET
from prometheus_client import start_http_server, Gauge
import time
from datetime import datetime
import argparse
import sys
import logging
from .version import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nova-libvirt-exporter')

class NovaLibvirtExporter:
    def __init__(self, port=9179, libvirt_uri='qemu:///system'):
        """
        Initialize the Nova Libvirt Exporter

        Args:
            port (int): The port to expose metrics on
            libvirt_uri (str): The libvirt connection URI
        """
        self.port = port
        self.libvirt_uri = libvirt_uri

        # Instance metadata metrics
        self.instance_metadata = Gauge('nova_instance_metadata', 'Nova instance metadata',
                                     ['instance_name', 'nova_name', 'creation_time', 'package_version'])

        self.flavor_metadata = Gauge('nova_flavor_metadata', 'Nova flavor metadata',
                                   ['instance_name', 'flavor_name', 'memory', 'disk', 'vcpus',
                                    'swap', 'ephemeral'])

        self.owner_metadata = Gauge('nova_owner_metadata', 'Nova owner metadata',
                                  ['instance_name', 'user', 'user_uuid', 'project', 'project_uuid'])

        # System metrics
        self.memory = Gauge('nova_instance_memory_kib', 'Instance memory in KiB',
                          ['instance_name', 'instance_uuid'])
        self.vcpus = Gauge('nova_instance_vcpus', 'Instance vCPUs',
                          ['instance_name', 'instance_uuid'])
        self.cpu_shares = Gauge('nova_instance_cpu_shares', 'CPU shares',
                              ['instance_name', 'instance_uuid'])

        # CPU topology metrics
        self.cpu_topology = Gauge('nova_instance_cpu_topology', 'CPU topology information',
                                ['instance_name', 'sockets', 'cores', 'threads', 'model'])

        # System info metrics
        self.sysinfo = Gauge('nova_instance_sysinfo', 'System information',
                            ['instance_name', 'manufacturer', 'product', 'version',
                             'serial', 'family'])

        # OS info metrics
        self.os_info = Gauge('nova_instance_os', 'Operating system information',
                            ['instance_name', 'arch', 'machine', 'type'])

        # Network metrics
        self.network_info = Gauge('nova_instance_network', 'Network interface information',
                                ['instance_name', 'mac_address', 'target_dev', 'model', 'mtu'])
        self.network_details = Gauge('nova_instance_network_details', 'Detailed network information',
                                   ['instance_name', 'mac_address', 'model', 'mtu',
                                    'target_dev', 'pci_slot'])
        self.ip_info = Gauge('nova_instance_ip', 'IP address information',
                           ['instance_name', 'port_uuid', 'ip_address', 'ip_version', 'type'])

        # Storage metrics
        self.disk_info = Gauge('nova_instance_disk', 'Disk information',
                             ['instance_name', 'device', 'type', 'driver_type', 'cache', 'path'])
        self.disk_details = Gauge('nova_instance_disk_details', 'Detailed disk information',
                                ['instance_name', 'device', 'size_bytes', 'backing_file',
                                 'target_bus', 'disk_type', 'disk_cache'])

        # PCI device metrics
        self.pci_device = Gauge('nova_instance_pci_device', 'PCI device information',
                              ['instance_name', 'source_bus', 'source_slot', 'source_function',
                               'target_bus', 'target_slot', 'target_function'])

        # Graphics metrics
        self.graphics_info = Gauge('nova_instance_graphics', 'Graphics configuration',
                                 ['instance_name', 'type', 'port', 'listen_address'])

        # Memory balloon metrics
        self.memballoon = Gauge('nova_instance_memballoon', 'Memory balloon device information',
                              ['instance_name', 'model', 'period'])

        # Root disk information
        self.root_disk_info = Gauge('nova_instance_root_disk', 'Root disk information',
                                   ['instance_name', 'type', 'uuid'])

        # Features enabled/disabled
        self.instance_features = Gauge('nova_instance_features', 'Instance features status',
                                     ['instance_name', 'feature_name', 'state'])

        # Console/Serial information
        self.console_info = Gauge('nova_instance_console', 'Console configuration',
                                ['instance_name', 'type', 'log_path'])

        # Input devices
        self.input_devices = Gauge('nova_instance_input_devices', 'Input devices configuration',
                                 ['instance_name', 'type', 'bus'])

        # Video card information
        self.video_info = Gauge('nova_instance_video', 'Video device information',
                              ['instance_name', 'model', 'vram', 'heads'])

        # RNG device information
        self.rng_info = Gauge('nova_instance_rng', 'Random number generator device information',
                             ['instance_name', 'model', 'backend'])

        # Power management actions
        self.power_management = Gauge('nova_instance_power_management', 'Power management configuration',
                                    ['instance_name', 'on_poweroff', 'on_reboot', 'on_crash'])

        # Boot configuration
        self.boot_config = Gauge('nova_instance_boot', 'Boot configuration',
                               ['instance_name', 'boot_device', 'boot_order'])

    def _get_sysinfo_entry(self, sysinfo, name):
        """Helper method to get sysinfo entries"""
        entry = sysinfo.find(f"entry[@name='{name}']")
        return entry.text if entry is not None else 'unknown'

    def parse_nova_metadata(self, metadata, instance_name):
        try:
            nova_ns = {'nova': 'http://openstack.org/xmlns/libvirt/nova/1.1'}
            instance = metadata.find('.//nova:instance', nova_ns)

            if instance is not None:
                # Basic instance info
                name = instance.find('nova:name', nova_ns)
                creation_time = instance.find('nova:creationTime', nova_ns)
                package = instance.find('nova:package', nova_ns)

                if all([name, creation_time, package]):
                    self.instance_metadata.labels(
                        instance_name=instance_name,
                        nova_name=name.text,
                        creation_time=creation_time.text,
                        package_version=package.get('version')
                    ).set(1)

                # Flavor info
                flavor = instance.find('.//nova:flavor', nova_ns)
                if flavor is not None:
                    self.flavor_metadata.labels(
                        instance_name=instance_name,
                        flavor_name=flavor.get('name'),
                        memory=flavor.find('nova:memory', nova_ns).text,
                        disk=flavor.find('nova:disk', nova_ns).text,
                        vcpus=flavor.find('nova:vcpus', nova_ns).text,
                        swap=flavor.find('nova:swap', nova_ns).text,
                        ephemeral=flavor.find('nova:ephemeral', nova_ns).text
                    ).set(1)

                # Owner info
                owner = instance.find('.//nova:owner', nova_ns)
                if owner is not None:
                    user = owner.find('nova:user', nova_ns)
                    project = owner.find('nova:project', nova_ns)
                    if user is not None and project is not None:
                        self.owner_metadata.labels(
                            instance_name=instance_name,
                            user=user.text,
                            user_uuid=user.get('uuid'),
                            project=project.text,
                            project_uuid=project.get('uuid')
                        ).set(1)

                # Network ports
                for port in instance.findall('.//nova:port', nova_ns):
                    port_uuid = port.get('uuid')
                    for ip in port.findall('nova:ip', nova_ns):
                        self.ip_info.labels(
                            instance_name=instance_name,
                            port_uuid=port_uuid,
                            ip_address=ip.get('address'),
                            ip_version=ip.get('ipVersion'),
                            type=ip.get('type')
                        ).set(1)

        except Exception as e:
            logger.error(f"Error parsing Nova metadata for {instance_name}: {str(e)}")

    def parse_domain(self, xml_str):
        try:
            root = ET.fromstring(xml_str)
            instance_name = root.findtext('name')
            instance_uuid = root.findtext('uuid')

            metadata = root.find('metadata')
            if metadata is not None:
                self.parse_nova_metadata(metadata, instance_name)

            # Memory and CPU metrics
            memory_kib = int(root.findtext('memory', '0'))
            self.memory.labels(
                instance_name=instance_name,
                instance_uuid=instance_uuid
            ).set(memory_kib)

            vcpus = int(root.findtext('vcpu', '0'))
            self.vcpus.labels(
                instance_name=instance_name,
                instance_uuid=instance_uuid
            ).set(vcpus)

            # CPU shares
            cputune = root.find('cputune')
            if cputune is not None:
                shares = int(cputune.findtext('shares', '0'))
                self.cpu_shares.labels(
                    instance_name=instance_name,
                    instance_uuid=instance_uuid
                ).set(shares)

            # CPU topology
            cpu = root.find('cpu')
            if cpu is not None:
                topology = cpu.find('topology')
                if topology is not None:
                    self.cpu_topology.labels(
                        instance_name=instance_name,
                        sockets=topology.get('sockets', '1'),
                        cores=topology.get('cores', '1'),
                        threads=topology.get('threads', '1'),
                        model=cpu.find('model').text if cpu.find('model') is not None else 'unknown'
                    ).set(1)

            # System information
            sysinfo = root.find('.//system')
            if sysinfo is not None:
                self.sysinfo.labels(
                    instance_name=instance_name,
                    manufacturer=self._get_sysinfo_entry(sysinfo, 'manufacturer'),
                    product=self._get_sysinfo_entry(sysinfo, 'product'),
                    version=self._get_sysinfo_entry(sysinfo, 'version'),
                    serial=self._get_sysinfo_entry(sysinfo, 'serial'),
                    family=self._get_sysinfo_entry(sysinfo, 'family')
                ).set(1)

            # OS information
            os_elem = root.find('os/type')
            if os_elem is not None:
                self.os_info.labels(
                    instance_name=instance_name,
                    arch=os_elem.get('arch', 'unknown'),
                    machine=os_elem.get('machine', 'unknown'),
                    type=os_elem.text
                ).set(1)

            # Devices section
            devices = root.find('devices')
            if devices is not None:
                # Network interfaces
                for interface in devices.findall('.//interface[@type="ethernet"]'):
                    mac = interface.find('mac')
                    target = interface.find('target')
                    model = interface.find('model')
                    mtu = interface.find('mtu')

                    if all([mac, target, model, mtu]):
                        self.network_info.labels(
                            instance_name=instance_name,
                            mac_address=mac.get('address'),
                            target_dev=target.get('dev'),
                            model=model.get('type'),
                            mtu=mtu.get('size')
                        ).set(1)

                # Disks
                for disk in devices.findall('.//disk[@type="file"]'):
                    driver = disk.find('driver')
                    target = disk.find('target')
                    source = disk.find('source')

                    if all([driver, target, source]):
                        self.disk_info.labels(
                            instance_name=instance_name,
                            device=target.get('dev'),
                            type=disk.get('type'),
                            driver_type=driver.get('type'),
                            cache=driver.get('cache'),
                            path=source.get('file')
                        ).set(1)

                        # Detailed disk information
                        self.disk_details.labels(
                            instance_name=instance_name,
                            device=target.get('dev'),
                            size_bytes=0,  # Would need additional libvirt calls to get actual size
                            backing_file=source.get('file', ''),
                            target_bus=target.get('bus', ''),
                            disk_type=driver.get('type', ''),
                            disk_cache=driver.get('cache', '')
                        ).set(1)

                # Network interface detailed information
                for interface in devices.findall('.//interface[@type="ethernet"]'):
                    address = interface.find('address')
                    mac = interface.find('mac')
                    model = interface.find('model')
                    mtu = interface.find('mtu')
                    target = interface.find('target')

                    if all([mac, model, mtu, target]):
                        self.network_details.labels(
                            instance_name=instance_name,
                            mac_address=mac.get('address'),
                            model=model.get('type'),
                            mtu=mtu.get('size'),
                            target_dev=target.get('dev'),
                            pci_slot=f"{address.get('bus')}:{address.get('slot')}" if address is not None else 'unknown'
                        ).set(1)
                # PCI devices
                logger.info(f"Looking for PCI devices in {instance_name}")
                hostdevs = devices.findall('.//hostdev[@type="pci"]')
                logger.info(f"Found {len(hostdevs)} PCI devices")
                for hostdev in hostdevs:
                    source = hostdev.find('source/address')
                    target = hostdev.find('address')

                    logger.info(f"Source: {source}, Target: {target}")
                    if source is not None and target is not None:
                        logger.info(f"Processing PCI device: source_bus={source.get('bus')}")
                        self.pci_device.labels(
                            instance_name=instance_name,
                            source_bus=source.get('bus'),
                            source_slot=source.get('slot'),
                            source_function=source.get('function'),
                            target_bus=target.get('bus'),
                            target_slot=target.get('slot'),
                            target_function=target.get('function')
                        ).set(1)

                # Graphics
                graphics = devices.find('graphics')
                listen = graphics.find('listen') if graphics is not None else None

                if graphics is not None and listen is not None:
                    self.graphics_info.labels(
                        instance_name=instance_name,
                        type=graphics.get('type'),
                        port=graphics.get('port'),
                        listen_address=listen.get('address')
                    ).set(1)

                # Memory balloon information
                memballoon = devices.find('.//memballoon')
                if memballoon is not None:
                    stats = memballoon.find('stats')
                    self.memballoon.labels(
                        instance_name=instance_name,
                        model=memballoon.get('model', 'unknown'),
                        period=stats.get('period') if stats is not None else '0'
                    ).set(1)

        except Exception as e:
            logger.error(f"Error parsing domain XML for {instance_name}: {str(e)}")

    def collect_metrics(self):
        """Collect metrics from libvirt"""
        try:
            conn = libvirt.open(self.libvirt_uri)
            if conn is None:
                raise Exception('Failed to connect to libvirt')

            domains = conn.listAllDomains()
            for domain in domains:
                xml = domain.XMLDesc()
                self.parse_domain(xml)

            conn.close()

        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")

    def run(self):
        """Run the exporter"""
        # Start up the server to expose metrics
        start_http_server(self.port)
        logger.info(f"Nova Libvirt Exporter v{__version__} starting up on port {self.port}")
        logger.info(f"Using libvirt connection: {self.libvirt_uri}")

        while True:
            self.collect_metrics()
            time.sleep(30)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Nova Libvirt Exporter')
    parser.add_argument('--port', type=int, default=9179,
                       help='Port to expose metrics on (default: 9179)')
    parser.add_argument('--libvirt-uri', default='qemu:///system',
                       help='Libvirt connection URI (default: qemu:///system)')
    parser.add_argument('--version', action='version',
                       version=f'Nova Libvirt Exporter v{__version__}')

    args = parser.parse_args()

    try:
        exporter = NovaLibvirtExporter(args.port, args.libvirt_uri)
        exporter.run()
    except KeyboardInterrupt:
        logger.info("Shutting down exporter")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
