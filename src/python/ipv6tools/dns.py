"""
IPv6 DNS utilities for AAAA record management and DNS operations.
"""

import socket
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass


@dataclass
class DNSRecord:
    """DNS record information."""
    hostname: str
    address: str
    record_type: str
    ttl: Optional[int] = None


class IPv6DNSTools:
    """Tools for IPv6 DNS operations."""

    @staticmethod
    def lookup_aaaa(hostname: str) -> List[str]:
        """
        Lookup AAAA records for a hostname.

        Args:
            hostname: Hostname to lookup

        Returns:
            List of IPv6 addresses

        Raises:
            socket.gaierror: If lookup fails
        """
        try:
            # Get address info for IPv6
            addrinfo = socket.getaddrinfo(
                hostname,
                None,
                family=socket.AF_INET6,
                type=socket.SOCK_STREAM
            )

            # Extract unique IPv6 addresses
            addresses = list(set(info[4][0] for info in addrinfo))
            return addresses

        except socket.gaierror as e:
            raise socket.gaierror(f"Failed to lookup {hostname}: {e}")

    @staticmethod
    def lookup_both(hostname: str) -> Dict[str, List[str]]:
        """
        Lookup both A and AAAA records.

        Args:
            hostname: Hostname to lookup

        Returns:
            Dict with 'ipv4' and 'ipv6' lists
        """
        result = {'ipv4': [], 'ipv6': []}

        try:
            # Get all addresses
            addrinfo = socket.getaddrinfo(hostname, None)

            for info in addrinfo:
                family = info[0]
                address = info[4][0]

                if family == socket.AF_INET:
                    if address not in result['ipv4']:
                        result['ipv4'].append(address)
                elif family == socket.AF_INET6:
                    # Remove zone ID if present
                    address = address.split('%')[0]
                    if address not in result['ipv6']:
                        result['ipv6'].append(address)

        except socket.gaierror:
            pass

        return result

    @staticmethod
    def reverse_lookup(address: str) -> Optional[str]:
        """
        Perform reverse DNS lookup (PTR record).

        Args:
            address: IPv6 address

        Returns:
            Hostname or None if not found
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(address)
            return hostname
        except (socket.herror, socket.gaierror):
            return None

    @staticmethod
    def has_ipv6(hostname: str) -> bool:
        """
        Check if hostname has IPv6 (AAAA record).

        Args:
            hostname: Hostname to check

        Returns:
            True if has IPv6
        """
        try:
            addresses = IPv6DNSTools.lookup_aaaa(hostname)
            return len(addresses) > 0
        except socket.gaierror:
            return False

    @staticmethod
    def prefer_ipv6(hostname: str) -> str:
        """
        Get preferred address for hostname (IPv6 if available).

        Args:
            hostname: Hostname to resolve

        Returns:
            IPv6 address if available, otherwise IPv4

        Raises:
            socket.gaierror: If no address found
        """
        records = IPv6DNSTools.lookup_both(hostname)

        if records['ipv6']:
            return records['ipv6'][0]
        elif records['ipv4']:
            return records['ipv4'][0]
        else:
            raise socket.gaierror(f"No addresses found for {hostname}")

    @staticmethod
    def generate_ptr_record(address: str) -> str:
        """
        Generate PTR record name for IPv6 address.

        Args:
            address: IPv6 address

        Returns:
            PTR record name (e.g., x.x.x...ip6.arpa)
        """
        from .utils import reverse_pointer
        return reverse_pointer(address)

    @staticmethod
    def batch_lookup(hostnames: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """
        Lookup multiple hostnames.

        Args:
            hostnames: List of hostnames

        Returns:
            Dict mapping hostname to address records
        """
        results = {}

        for hostname in hostnames:
            try:
                results[hostname] = IPv6DNSTools.lookup_both(hostname)
            except Exception as e:
                results[hostname] = {'error': str(e), 'ipv4': [], 'ipv6': []}

        return results

    @staticmethod
    def test_connectivity(hostname: str, port: int = 80, timeout: float = 5.0) -> Tuple[bool, Optional[str]]:
        """
        Test IPv6 connectivity to hostname.

        Args:
            hostname: Hostname to test
            port: Port to test
            timeout: Connection timeout

        Returns:
            Tuple of (success, address_used)
        """
        try:
            addresses = IPv6DNSTools.lookup_aaaa(hostname)

            for address in addresses:
                try:
                    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    sock.connect((address, port))
                    sock.close()
                    return True, address
                except (socket.timeout, socket.error):
                    continue

            return False, None

        except socket.gaierror:
            return False, None

    @staticmethod
    def compare_dual_stack(hostname: str) -> Dict[str, any]:
        """
        Compare IPv4 and IPv6 connectivity.

        Args:
            hostname: Hostname to test

        Returns:
            Dict with comparison results
        """
        records = IPv6DNSTools.lookup_both(hostname)

        result = {
            'hostname': hostname,
            'has_ipv4': len(records['ipv4']) > 0,
            'has_ipv6': len(records['ipv6']) > 0,
            'ipv4_addresses': records['ipv4'],
            'ipv6_addresses': records['ipv6'],
            'is_dual_stack': len(records['ipv4']) > 0 and len(records['ipv6']) > 0,
            'is_ipv6_only': len(records['ipv4']) == 0 and len(records['ipv6']) > 0,
            'is_ipv4_only': len(records['ipv4']) > 0 and len(records['ipv6']) == 0,
        }

        return result


def dns_cli():
    """Command-line interface for DNS tools."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="IPv6 DNS Tools")
    parser.add_argument("hostname", nargs="+", help="Hostname(s) to lookup")
    parser.add_argument("-r", "--reverse", action="store_true", help="Reverse lookup (PTR)")
    parser.add_argument("-4", "--ipv4", action="store_true", help="Show IPv4 addresses")
    parser.add_argument("-6", "--ipv6", action="store_true", help="Show only IPv6 addresses")
    parser.add_argument("-c", "--compare", action="store_true", help="Compare dual-stack")
    parser.add_argument("-t", "--test", type=int, metavar="PORT", help="Test connectivity on port")

    args = parser.parse_args()

    tools = IPv6DNSTools()

    for hostname in args.hostname:
        print(f"\n=== {hostname} ===")

        if args.reverse:
            # Reverse lookup
            ptr = tools.reverse_lookup(hostname)
            if ptr:
                print(f"PTR: {ptr}")
            else:
                print("No PTR record found")
        elif args.compare:
            # Dual-stack comparison
            result = tools.compare_dual_stack(hostname)
            print(f"IPv4: {', '.join(result['ipv4_addresses']) if result['has_ipv4'] else 'None'}")
            print(f"IPv6: {', '.join(result['ipv6_addresses']) if result['has_ipv6'] else 'None'}")
            print(f"Type: {'Dual-stack' if result['is_dual_stack'] else 'IPv6-only' if result['is_ipv6_only'] else 'IPv4-only'}")
        elif args.test:
            # Test connectivity
            success, address = tools.test_connectivity(hostname, args.test)
            if success:
                print(f"✓ Connected to {address}:{args.test}")
            else:
                print(f"✗ Failed to connect on port {args.test}")
        else:
            # Normal lookup
            records = tools.lookup_both(hostname)

            if args.ipv4 and records['ipv4']:
                print("IPv4 (A):")
                for addr in records['ipv4']:
                    print(f"  {addr}")

            if not args.ipv4:  # Show IPv6 by default or with -6
                if records['ipv6']:
                    print("IPv6 (AAAA):")
                    for addr in records['ipv6']:
                        print(f"  {addr}")
                else:
                    print("No IPv6 addresses found")


if __name__ == "__main__":
    dns_cli()
