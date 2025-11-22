"""
IPv6 network simulation and testing framework.
"""

import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .address import IPv6Address, IPv6Network
from .utils import generate_link_local, generate_unique_local, mac_to_ipv6_link_local


@dataclass
class SimulatedHost:
    """Simulated network host."""
    name: str
    mac: str
    link_local: str
    global_addresses: List[str] = field(default_factory=list)
    routes: List[str] = field(default_factory=list)
    is_router: bool = False


@dataclass
class SimulatedNetwork:
    """Simulated IPv6 network."""
    prefix: str
    hosts: List[SimulatedHost] = field(default_factory=list)
    router: Optional[SimulatedHost] = None
    vlan_id: Optional[int] = None


class IPv6NetworkSimulator:
    """Simulate IPv6 network environments for testing."""

    def __init__(self):
        """Initialize simulator."""
        self.networks: List[SimulatedNetwork] = []
        self.hosts: List[SimulatedHost] = []

    def generate_mac(self) -> str:
        """Generate random MAC address."""
        mac = [random.randint(0x00, 0xff) for _ in range(6)]
        # Set locally administered bit
        mac[0] |= 0x02
        return ':'.join(f'{b:02x}' for b in mac)

    def create_host(self, name: str, mac: Optional[str] = None) -> SimulatedHost:
        """
        Create a simulated host.

        Args:
            name: Host name
            mac: MAC address (generated if not provided)

        Returns:
            SimulatedHost
        """
        if mac is None:
            mac = self.generate_mac()

        # Generate link-local from MAC
        link_local = mac_to_ipv6_link_local(mac)

        host = SimulatedHost(
            name=name,
            mac=mac,
            link_local=link_local,
        )

        self.hosts.append(host)
        return host

    def create_router(self, name: str) -> SimulatedHost:
        """Create a router."""
        router = self.create_host(name)
        router.is_router = True
        return router

    def create_network(self, prefix: str, num_hosts: int = 5) -> SimulatedNetwork:
        """
        Create a simulated network with hosts.

        Args:
            prefix: Network prefix (e.g., "2001:db8::/64")
            num_hosts: Number of hosts to create

        Returns:
            SimulatedNetwork
        """
        network = SimulatedNetwork(prefix=prefix)

        # Create router
        router = self.create_router(f"router-{len(self.networks)}")
        network.router = router

        # Add router global address
        net = IPv6Network(prefix, strict=False)
        router_addr = str(net.network_address).rstrip(':') + '::1'
        router.global_addresses.append(router_addr)

        # Create hosts
        for i in range(num_hosts):
            host = self.create_host(f"host-{i+1}")

            # Assign global address (SLAAC-like)
            # Use random interface ID
            interface_id = f"{random.randint(0, 0xffff):04x}:{random.randint(0, 0xffff):04x}:{random.randint(0, 0xffff):04x}:{random.randint(0, 0xffff):04x}"
            host_addr = str(net.network_address).rstrip(':') + '::' + interface_id

            try:
                # Validate it's in network
                if net.contains(host_addr):
                    host.global_addresses.append(host_addr)
            except:
                pass

            # Add default route
            host.routes.append(f"default via {router_addr}")

            network.hosts.append(host)

        self.networks.append(network)
        return network

    def create_dual_stack_network(self, ipv6_prefix: str, ipv4_subnet: str) -> Dict:
        """
        Create dual-stack network simulation.

        Args:
            ipv6_prefix: IPv6 prefix
            ipv4_subnet: IPv4 subnet

        Returns:
            Dict with network information
        """
        network = self.create_network(ipv6_prefix)

        return {
            'type': 'dual-stack',
            'ipv6_prefix': ipv6_prefix,
            'ipv4_subnet': ipv4_subnet,
            'network': network,
            'hosts': network.hosts,
            'router': network.router
        }

    def create_site(self, site_prefix: str, num_vlans: int = 3) -> Dict[str, any]:
        """
        Create a site with multiple VLANs.

        Args:
            site_prefix: Site prefix (e.g., "2001:db8::/48")
            num_vlans: Number of VLANs

        Returns:
            Dict with site information
        """
        site = {
            'prefix': site_prefix,
            'vlans': []
        }

        net = IPv6Network(site_prefix, strict=False)
        base_prefix = net.prefix_length

        # Create VLANs
        for i in range(num_vlans):
            # Calculate /64 for each VLAN
            vlan_prefix = f"{str(net.network_address).rstrip(':')}:{i:x}::/64"

            vlan_net = self.create_network(vlan_prefix, num_hosts=random.randint(3, 10))
            vlan_net.vlan_id = i + 1

            site['vlans'].append({
                'id': i + 1,
                'prefix': vlan_prefix,
                'network': vlan_net
            })

        return site

    def simulate_traffic(self, source: SimulatedHost, destination: SimulatedHost) -> Dict[str, any]:
        """
        Simulate traffic between hosts.

        Args:
            source: Source host
            destination: Destination host

        Returns:
            Dict with traffic simulation results
        """
        # Determine which addresses to use
        src_addr = source.global_addresses[0] if source.global_addresses else source.link_local
        dst_addr = destination.global_addresses[0] if destination.global_addresses else destination.link_local

        # Check if on same network (simplified)
        same_network = src_addr.split(':')[0:4] == dst_addr.split(':')[0:4]

        hops = []

        if same_network:
            # Direct communication
            hops = [
                {'hop': 1, 'address': src_addr, 'type': 'source'},
                {'hop': 2, 'address': dst_addr, 'type': 'destination'}
            ]
        else:
            # Via router
            # Find router
            router_addr = "fe80::1"  # Simplified

            hops = [
                {'hop': 1, 'address': src_addr, 'type': 'source'},
                {'hop': 2, 'address': router_addr, 'type': 'router'},
                {'hop': 3, 'address': dst_addr, 'type': 'destination'}
            ]

        return {
            'source': {'name': source.name, 'address': src_addr},
            'destination': {'name': destination.name, 'address': dst_addr},
            'path': hops,
            'same_network': same_network
        }

    def generate_report(self) -> str:
        """Generate network simulation report."""
        report = []
        report.append("=" * 80)
        report.append("IPv6 NETWORK SIMULATION REPORT")
        report.append("=" * 80)
        report.append("")

        report.append(f"Total Networks: {len(self.networks)}")
        report.append(f"Total Hosts: {len(self.hosts)}")
        report.append("")

        for i, network in enumerate(self.networks, 1):
            report.append(f"\nNetwork {i}: {network.prefix}")
            report.append("-" * 80)

            if network.router:
                report.append(f"\nRouter: {network.router.name}")
                report.append(f"  MAC: {network.router.mac}")
                report.append(f"  Link-local: {network.router.link_local}")
                if network.router.global_addresses:
                    report.append(f"  Global: {', '.join(network.router.global_addresses)}")

            report.append(f"\nHosts ({len(network.hosts)}):")
            for host in network.hosts:
                report.append(f"\n  {host.name}")
                report.append(f"    MAC: {host.mac}")
                report.append(f"    Link-local: {host.link_local}")
                if host.global_addresses:
                    report.append(f"    Global: {', '.join(host.global_addresses)}")
                if host.routes:
                    report.append(f"    Routes: {len(host.routes)}")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def export_config(self, host: SimulatedHost) -> str:
        """
        Export configuration for a host.

        Args:
            host: Host to export config for

        Returns:
            Configuration string
        """
        config = []
        config.append(f"# Configuration for {host.name}")
        config.append(f"# MAC: {host.mac}")
        config.append("")

        config.append("# IPv6 Addresses")
        config.append(f"ip -6 addr add {host.link_local}/64 dev eth0")

        for addr in host.global_addresses:
            config.append(f"ip -6 addr add {addr}/64 dev eth0")

        if host.routes:
            config.append("\n# IPv6 Routes")
            for route in host.routes:
                config.append(f"ip -6 route add {route}")

        return "\n".join(config)


def simulator_cli():
    """Command-line interface for simulator."""
    import argparse

    parser = argparse.ArgumentParser(description="IPv6 Network Simulator")
    parser.add_argument("-n", "--network", default="2001:db8::/64",
                       help="Network prefix")
    parser.add_argument("-H", "--hosts", type=int, default=5,
                       help="Number of hosts")
    parser.add_argument("-s", "--site", action="store_true",
                       help="Create site with multiple VLANs")
    parser.add_argument("-v", "--vlans", type=int, default=3,
                       help="Number of VLANs (for site mode)")

    args = parser.parse_args()

    sim = IPv6NetworkSimulator()

    if args.site:
        print(f"Creating site simulation with {args.vlans} VLANs...")
        site = sim.create_site(args.network, args.vlans)

        print(f"\nSite: {site['prefix']}")
        print(f"VLANs: {len(site['vlans'])}")

        for vlan in site['vlans']:
            print(f"\n  VLAN {vlan['id']}: {vlan['prefix']}")
            print(f"    Hosts: {len(vlan['network'].hosts)}")

    else:
        print(f"Creating network simulation...")
        network = sim.create_network(args.network, args.hosts)

        print(f"\nNetwork: {network.prefix}")
        print(f"Router: {network.router.name}")
        print(f"Hosts: {len(network.hosts)}")

    print("\n" + sim.generate_report())


if __name__ == "__main__":
    simulator_cli()
