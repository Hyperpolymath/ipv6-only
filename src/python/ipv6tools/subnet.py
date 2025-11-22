"""
IPv6 subnet calculator and network planning utilities.
"""

import ipaddress
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SubnetInfo:
    """Information about a subnet."""
    network: str
    network_address: str
    first_address: str
    last_address: str
    prefix_length: int
    num_addresses: int
    netmask: str


class IPv6SubnetCalculator:
    """
    Calculator for IPv6 subnet operations and planning.
    """

    def __init__(self, network: str):
        """
        Initialize subnet calculator with a network.

        Args:
            network: IPv6 network in CIDR notation

        Raises:
            ValueError: If network is invalid
        """
        try:
            self.network = ipaddress.IPv6Network(network, strict=False)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
            raise ValueError(f"Invalid network: {e}")

    def get_info(self) -> SubnetInfo:
        """
        Get detailed information about the network.

        Returns:
            SubnetInfo object with network details
        """
        return SubnetInfo(
            network=str(self.network),
            network_address=str(self.network.network_address),
            first_address=str(self.network.network_address),
            last_address=str(self.network.broadcast_address),
            prefix_length=self.network.prefixlen,
            num_addresses=self.network.num_addresses,
            netmask=str(self.network.netmask)
        )

    def divide_into_subnets(self, num_subnets: int) -> List[SubnetInfo]:
        """
        Divide the network into a specified number of subnets.

        Args:
            num_subnets: Number of subnets to create

        Returns:
            List of SubnetInfo objects

        Raises:
            ValueError: If division is not possible
        """
        if num_subnets < 1:
            raise ValueError("Number of subnets must be at least 1")

        # Calculate required prefix length
        import math
        bits_needed = math.ceil(math.log2(num_subnets))
        new_prefix = self.network.prefixlen + bits_needed

        if new_prefix > 128:
            raise ValueError(f"Cannot divide into {num_subnets} subnets - would exceed /128")

        # Generate subnets
        subnets = list(self.network.subnets(prefixlen_diff=bits_needed))[:num_subnets]

        return [
            SubnetInfo(
                network=str(subnet),
                network_address=str(subnet.network_address),
                first_address=str(subnet.network_address),
                last_address=str(subnet.broadcast_address),
                prefix_length=subnet.prefixlen,
                num_addresses=subnet.num_addresses,
                netmask=str(subnet.netmask)
            )
            for subnet in subnets
        ]

    def divide_by_prefix(self, new_prefix: int) -> List[SubnetInfo]:
        """
        Divide the network by specifying new prefix length.

        Args:
            new_prefix: New prefix length for subnets

        Returns:
            List of SubnetInfo objects

        Raises:
            ValueError: If new prefix is invalid
        """
        if new_prefix <= self.network.prefixlen:
            raise ValueError(f"New prefix must be larger than current prefix /{self.network.prefixlen}")

        if new_prefix > 128:
            raise ValueError("Prefix length cannot exceed 128")

        prefixlen_diff = new_prefix - self.network.prefixlen
        subnets = list(self.network.subnets(prefixlen_diff=prefixlen_diff))

        return [
            SubnetInfo(
                network=str(subnet),
                network_address=str(subnet.network_address),
                first_address=str(subnet.network_address),
                last_address=str(subnet.broadcast_address),
                prefix_length=subnet.prefixlen,
                num_addresses=subnet.num_addresses,
                netmask=str(subnet.netmask)
            )
            for subnet in subnets
        ]

    def get_supernet(self, new_prefix: int) -> SubnetInfo:
        """
        Get the supernet with specified prefix length.

        Args:
            new_prefix: New prefix length (must be smaller)

        Returns:
            SubnetInfo for the supernet

        Raises:
            ValueError: If new prefix is invalid
        """
        if new_prefix >= self.network.prefixlen:
            raise ValueError(f"New prefix must be smaller than current prefix /{self.network.prefixlen}")

        if new_prefix < 0:
            raise ValueError("Prefix length cannot be negative")

        prefixlen_diff = self.network.prefixlen - new_prefix
        supernet = self.network.supernet(prefixlen_diff=prefixlen_diff)

        return SubnetInfo(
            network=str(supernet),
            network_address=str(supernet.network_address),
            first_address=str(supernet.network_address),
            last_address=str(supernet.broadcast_address),
            prefix_length=supernet.prefixlen,
            num_addresses=supernet.num_addresses,
            netmask=str(supernet.netmask)
        )

    def contains_address(self, address: str) -> bool:
        """
        Check if an address is within this network.

        Args:
            address: IPv6 address to check

        Returns:
            True if address is in network
        """
        try:
            # Remove zone ID if present
            clean_addr = address.split('%')[0]
            addr = ipaddress.IPv6Address(clean_addr)
            return addr in self.network
        except (ipaddress.AddressValueError, ValueError):
            return False

    def overlaps_with(self, other_network: str) -> bool:
        """
        Check if this network overlaps with another.

        Args:
            other_network: Another IPv6 network in CIDR notation

        Returns:
            True if networks overlap
        """
        try:
            other = ipaddress.IPv6Network(other_network, strict=False)
            return self.network.overlaps(other)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            return False

    def get_summary_address(self, other_networks: List[str]) -> Optional[str]:
        """
        Calculate summary address (supernet) for multiple networks.

        Args:
            other_networks: List of IPv6 networks to summarize together with this one

        Returns:
            Summary network in CIDR notation, or None if cannot summarize

        Raises:
            ValueError: If any network is invalid
        """
        networks = [self.network]

        for net_str in other_networks:
            try:
                networks.append(ipaddress.IPv6Network(net_str, strict=False))
            except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
                raise ValueError(f"Invalid network {net_str}: {e}")

        # Use ipaddress.collapse_addresses to find optimal summary
        collapsed = list(ipaddress.collapse_addresses(networks))

        if len(collapsed) == 1:
            return str(collapsed[0])
        else:
            # Networks cannot be summarized into a single prefix
            # Return the smallest supernet that contains all
            min_addr = min(net.network_address for net in networks)
            max_addr = max(net.broadcast_address for net in networks)

            # Find common prefix length
            for prefix_len in range(0, 129):
                test_network = ipaddress.IPv6Network(f"{min_addr}/{prefix_len}", strict=False)
                if test_network.broadcast_address >= max_addr:
                    return str(test_network)

            return None

    @staticmethod
    def recommend_allocation(total_prefix: str, department_counts: Dict[str, int]) -> Dict[str, List[SubnetInfo]]:
        """
        Recommend subnet allocation based on department sizes.

        Args:
            total_prefix: Total IPv6 prefix to allocate from
            department_counts: Dict mapping department names to number of subnets needed

        Returns:
            Dict mapping department names to their allocated subnets

        Raises:
            ValueError: If allocation is not possible
        """
        network = ipaddress.IPv6Network(total_prefix, strict=False)

        # Calculate total subnets needed
        total_needed = sum(department_counts.values())

        # Find appropriate prefix length
        import math
        bits_needed = math.ceil(math.log2(total_needed))
        subnet_prefix = network.prefixlen + bits_needed

        if subnet_prefix > 128:
            raise ValueError(f"Cannot allocate {total_needed} subnets from {total_prefix}")

        # Generate all subnets
        all_subnets = list(network.subnets(prefixlen_diff=bits_needed))

        # Allocate to departments
        allocation = {}
        current_index = 0

        for dept_name, count in sorted(department_counts.items()):
            if current_index + count > len(all_subnets):
                raise ValueError(f"Not enough subnets for department {dept_name}")

            dept_subnets = []
            for i in range(count):
                subnet = all_subnets[current_index]
                dept_subnets.append(SubnetInfo(
                    network=str(subnet),
                    network_address=str(subnet.network_address),
                    first_address=str(subnet.network_address),
                    last_address=str(subnet.broadcast_address),
                    prefix_length=subnet.prefixlen,
                    num_addresses=subnet.num_addresses,
                    netmask=str(subnet.netmask)
                ))
                current_index += 1

            allocation[dept_name] = dept_subnets

        return allocation
