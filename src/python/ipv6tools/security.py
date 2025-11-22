"""
IPv6 security scanning and analysis tools.
"""

import socket
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import concurrent.futures
from .address import IPv6Address, IPv6Network
from .validator import is_valid_ipv6


@dataclass
class PortScanResult:
    """Result of port scan."""
    address: str
    port: int
    is_open: bool
    service: Optional[str] = None
    banner: Optional[str] = None
    response_time: Optional[float] = None


@dataclass
class SecurityScanResult:
    """Result of security scan."""
    address: str
    open_ports: List[int]
    vulnerabilities: List[str]
    warnings: List[str]
    info: Dict[str, any]


class IPv6SecurityScanner:
    """Security scanner for IPv6 networks."""

    # Common service ports
    COMMON_PORTS = [
        21,    # FTP
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        53,    # DNS
        80,    # HTTP
        110,   # POP3
        143,   # IMAP
        443,   # HTTPS
        445,   # SMB
        3306,  # MySQL
        3389,  # RDP
        5432,  # PostgreSQL
        8080,  # HTTP Alt
        8443,  # HTTPS Alt
    ]

    def __init__(self, timeout: float = 2.0, max_workers: int = 50):
        """
        Initialize scanner.

        Args:
            timeout: Connection timeout in seconds
            max_workers: Maximum concurrent workers
        """
        self.timeout = timeout
        self.max_workers = max_workers

    def scan_port(self, address: str, port: int) -> PortScanResult:
        """
        Scan a single port.

        Args:
            address: IPv6 address
            port: Port number

        Returns:
            PortScanResult
        """
        start_time = time.time()
        is_open = False
        banner = None

        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # Try to connect
            result = sock.connect_ex((address, port))
            is_open = (result == 0)

            if is_open:
                # Try to grab banner
                try:
                    sock.send(b"\r\n")
                    banner_bytes = sock.recv(1024)
                    banner = banner_bytes.decode('utf-8', errors='ignore').strip()
                except:
                    pass

            sock.close()

        except socket.error:
            pass

        response_time = time.time() - start_time

        return PortScanResult(
            address=address,
            port=port,
            is_open=is_open,
            service=self._get_service_name(port),
            banner=banner if banner else None,
            response_time=response_time if is_open else None
        )

    def scan_ports(self, address: str, ports: List[int]) -> List[PortScanResult]:
        """
        Scan multiple ports on an address.

        Args:
            address: IPv6 address
            ports: List of ports to scan

        Returns:
            List of PortScanResult
        """
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.scan_port, address, port): port for port in ports}

            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        return sorted(results, key=lambda x: x.port)

    def quick_scan(self, address: str) -> List[PortScanResult]:
        """
        Quick scan of common ports.

        Args:
            address: IPv6 address

        Returns:
            List of open ports
        """
        return [r for r in self.scan_ports(address, self.COMMON_PORTS) if r.is_open]

    def full_scan(self, address: str) -> List[PortScanResult]:
        """
        Full scan of all ports (1-1024).

        Args:
            address: IPv6 address

        Returns:
            List of open ports
        """
        ports = list(range(1, 1025))
        return [r for r in self.scan_ports(address, ports) if r.is_open]

    def security_audit(self, address: str) -> SecurityScanResult:
        """
        Perform security audit on address.

        Args:
            address: IPv6 address

        Returns:
            SecurityScanResult
        """
        vulnerabilities = []
        warnings = []
        info = {}

        # Scan common ports
        open_ports = self.quick_scan(address)
        port_numbers = [p.port for p in open_ports]

        # Check for security issues
        if 23 in port_numbers:
            vulnerabilities.append("Telnet (port 23) is open - unencrypted protocol")

        if 21 in port_numbers:
            warnings.append("FTP (port 21) is open - consider SFTP instead")

        if 80 in port_numbers and 443 not in port_numbers:
            warnings.append("HTTP without HTTPS - consider enabling TLS")

        if 3389 in port_numbers:
            warnings.append("RDP (port 3389) exposed - ensure strong authentication")

        if 22 in port_numbers:
            info['ssh_available'] = True

        if 443 in port_numbers:
            info['https_available'] = True

        # Check for common database ports
        db_ports = {3306: 'MySQL', 5432: 'PostgreSQL', 1433: 'MSSQL', 27017: 'MongoDB'}
        exposed_dbs = [db for port, db in db_ports.items() if port in port_numbers]
        if exposed_dbs:
            warnings.append(f"Database ports exposed: {', '.join(exposed_dbs)}")

        return SecurityScanResult(
            address=address,
            open_ports=port_numbers,
            vulnerabilities=vulnerabilities,
            warnings=warnings,
            info=info
        )

    def scan_network(self, network: str, quick: bool = True) -> List[Tuple[str, List[PortScanResult]]]:
        """
        Scan multiple addresses in a network.

        Args:
            network: IPv6 network in CIDR notation
            quick: If True, only scan common ports

        Returns:
            List of (address, open_ports) tuples
        """
        results = []

        # For demonstration, scan first few addresses
        # In production, use smarter host discovery
        net = IPv6Network(network, strict=False)
        base_addr = str(net.network_address)

        # Scan a few common patterns
        addresses_to_scan = [base_addr]

        # Add some common host IDs
        for host_id in [1, 2, 10, 100, 254]:
            # This is simplified - real implementation would properly manipulate IPv6 addresses
            pass

        for addr in addresses_to_scan:
            if is_valid_ipv6(addr):
                if quick:
                    open_ports = self.quick_scan(addr)
                else:
                    open_ports = self.full_scan(addr)

                if open_ports:
                    results.append((addr, open_ports))

        return results

    @staticmethod
    def _get_service_name(port: int) -> str:
        """Get service name for port."""
        services = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt',
        }
        return services.get(port, 'Unknown')

    def check_ipv6_specific_issues(self, address: str) -> List[str]:
        """
        Check for IPv6-specific security issues.

        Args:
            address: IPv6 address

        Returns:
            List of issues found
        """
        issues = []
        addr = IPv6Address(address)

        # Check for link-local in unexpected context
        if addr.is_link_local:
            issues.append("Link-local address detected - should not be globally routable")

        # Check for deprecated addresses
        if addr.is_reserved and not addr.is_loopback:
            issues.append("Reserved address space - may indicate misconfiguration")

        # Check for multicast
        if addr.is_multicast:
            issues.append("Multicast address - ensure intentional")

        return issues

    def privacy_check(self, address: str) -> Dict[str, any]:
        """
        Check if address uses privacy extensions.

        Args:
            address: IPv6 address

        Returns:
            Dict with privacy information
        """
        addr = IPv6Address(address)

        # Get interface ID (last 64 bits)
        expanded = addr.exploded
        groups = expanded.split(':')
        interface_id = ':'.join(groups[4:])

        # Check for patterns indicating privacy extensions
        # Privacy addresses are random, not based on MAC
        is_likely_eui64 = 'fffe' in interface_id.lower()
        is_likely_privacy = not is_likely_eui64 and not interface_id.endswith('0001')

        return {
            'address': address,
            'interface_id': interface_id,
            'likely_eui64': is_likely_eui64,
            'likely_privacy_extension': is_likely_privacy,
            'recommendation': 'Enable privacy extensions' if is_likely_eui64 else 'Privacy extensions likely enabled'
        }


def security_cli():
    """Command-line interface for security tools."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="IPv6 Security Scanner")
    parser.add_argument("target", help="IPv6 address or network to scan")
    parser.add_argument("-p", "--ports", help="Ports to scan (comma-separated)")
    parser.add_argument("-q", "--quick", action="store_true", help="Quick scan (common ports)")
    parser.add_argument("-f", "--full", action="store_true", help="Full scan (ports 1-1024)")
    parser.add_argument("-a", "--audit", action="store_true", help="Security audit")
    parser.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout (seconds)")
    parser.add_argument("-w", "--workers", type=int, default=50, help="Concurrent workers")

    args = parser.parse_args()

    scanner = IPv6SecurityScanner(timeout=args.timeout, max_workers=args.workers)

    if args.audit:
        # Security audit
        print(f"Security audit of {args.target}...\n")
        result = scanner.security_audit(args.target)

        print(f"Open ports: {', '.join(map(str, result.open_ports)) if result.open_ports else 'None'}")

        if result.vulnerabilities:
            print("\nVulnerabilities:")
            for vuln in result.vulnerabilities:
                print(f"  ❌ {vuln}")

        if result.warnings:
            print("\nWarnings:")
            for warn in result.warnings:
                print(f"  ⚠️  {warn}")

        if result.info:
            print("\nInformation:")
            for key, value in result.info.items():
                print(f"  ℹ️  {key}: {value}")

    else:
        # Port scan
        if args.ports:
            ports = [int(p.strip()) for p in args.ports.split(',')]
            results = scanner.scan_ports(args.target, ports)
        elif args.full:
            print("Running full scan (this may take a while)...")
            results = scanner.full_scan(args.target)
        else:
            print("Running quick scan...")
            results = scanner.quick_scan(args.target)

        open_results = [r for r in results if r.is_open]

        if open_results:
            print(f"\nOpen ports on {args.target}:")
            for result in open_results:
                banner_info = f" - {result.banner}" if result.banner else ""
                print(f"  {result.port:5d} {result.service:15s} [{result.response_time:.3f}s]{banner_info}")
        else:
            print(f"No open ports found on {args.target}")


if __name__ == "__main__":
    security_cli()
