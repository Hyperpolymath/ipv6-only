"""
IPv6 Address and Network classes for manipulation and analysis.
"""

import re
import ipaddress
from typing import Optional, List, Tuple


class IPv6Address:
    """
    Represents an IPv6 address with utilities for manipulation and analysis.
    """

    def __init__(self, address: str):
        """
        Initialize an IPv6 address.

        Args:
            address: IPv6 address string (compressed or expanded)

        Raises:
            ValueError: If address is invalid
        """
        # Remove zone ID if present (e.g., fe80::1%eth0)
        self.zone_id = None
        if '%' in address:
            address, self.zone_id = address.split('%', 1)

        try:
            self._addr = ipaddress.IPv6Address(address)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv6 address: {e}")

        self.address = str(self._addr)

    @property
    def compressed(self) -> str:
        """Return compressed form of the address."""
        return self._addr.compressed

    @property
    def exploded(self) -> str:
        """Return fully expanded form of the address."""
        return self._addr.exploded

    @property
    def is_link_local(self) -> bool:
        """Check if address is link-local (fe80::/10)."""
        return self._addr.is_link_local

    @property
    def is_loopback(self) -> bool:
        """Check if address is loopback (::1)."""
        return self._addr.is_loopback

    @property
    def is_multicast(self) -> bool:
        """Check if address is multicast (ff00::/8)."""
        return self._addr.is_multicast

    @property
    def is_global(self) -> bool:
        """Check if address is global unicast."""
        return self._addr.is_global

    @property
    def is_private(self) -> bool:
        """Check if address is unique local (fc00::/7)."""
        return self._addr.is_private

    @property
    def is_reserved(self) -> bool:
        """Check if address is reserved."""
        return self._addr.is_reserved

    @property
    def is_unspecified(self) -> bool:
        """Check if address is unspecified (::)."""
        return self._addr.is_unspecified

    def to_binary(self) -> str:
        """Convert address to binary representation."""
        return bin(int(self._addr))[2:].zfill(128)

    def to_hex(self) -> str:
        """Convert address to hexadecimal representation."""
        return hex(int(self._addr))[2:].zfill(32)

    def get_address_type(self) -> str:
        """
        Determine the type of IPv6 address.

        Returns:
            String describing the address type
        """
        if self.is_loopback:
            return "Loopback"
        elif self.is_link_local:
            return "Link-Local"
        elif self.is_private:
            return "Unique Local (ULA)"
        elif self.is_multicast:
            return "Multicast"
        elif self.is_global:
            return "Global Unicast"
        elif self.is_unspecified:
            return "Unspecified"
        elif self.is_reserved:
            return "Reserved"
        else:
            return "Unknown"

    def __str__(self) -> str:
        """String representation."""
        addr_str = self.compressed
        if self.zone_id:
            addr_str += f"%{self.zone_id}"
        return addr_str

    def __repr__(self) -> str:
        """Developer representation."""
        return f"IPv6Address('{str(self)}')"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if isinstance(other, IPv6Address):
            return self._addr == other._addr
        return False


class IPv6Network:
    """
    Represents an IPv6 network with CIDR notation.
    """

    def __init__(self, network: str, strict: bool = True):
        """
        Initialize an IPv6 network.

        Args:
            network: Network in CIDR notation (e.g., "2001:db8::/32")
            strict: If True, host bits must be zero

        Raises:
            ValueError: If network is invalid
        """
        try:
            self._network = ipaddress.IPv6Network(network, strict=strict)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
            raise ValueError(f"Invalid IPv6 network: {e}")

    @property
    def network_address(self) -> IPv6Address:
        """Get network address."""
        return IPv6Address(str(self._network.network_address))

    @property
    def broadcast_address(self) -> IPv6Address:
        """Get broadcast address (last address in network)."""
        return IPv6Address(str(self._network.broadcast_address))

    @property
    def netmask(self) -> str:
        """Get network mask."""
        return str(self._network.netmask)

    @property
    def hostmask(self) -> str:
        """Get host mask."""
        return str(self._network.hostmask)

    @property
    def prefix_length(self) -> int:
        """Get prefix length."""
        return self._network.prefixlen

    @property
    def num_addresses(self) -> int:
        """Get total number of addresses in network."""
        return self._network.num_addresses

    def hosts(self) -> List[IPv6Address]:
        """
        Generate all host addresses in the network.
        Warning: Can be very large for small prefix lengths!
        """
        if self.prefix_length < 64:
            raise ValueError("Network too large to enumerate hosts (prefix < /64)")
        return [IPv6Address(str(addr)) for addr in self._network.hosts()]

    def subnets(self, prefixlen_diff: int = 1) -> List['IPv6Network']:
        """
        Generate subnets by dividing this network.

        Args:
            prefixlen_diff: How many bits to add to prefix length

        Returns:
            List of subnet networks
        """
        return [IPv6Network(str(subnet)) for subnet in self._network.subnets(prefixlen_diff=prefixlen_diff)]

    def supernet(self, prefixlen_diff: int = 1) -> 'IPv6Network':
        """
        Get supernet by reducing prefix length.

        Args:
            prefixlen_diff: How many bits to subtract from prefix length

        Returns:
            Supernet network
        """
        return IPv6Network(str(self._network.supernet(prefixlen_diff=prefixlen_diff)))

    def contains(self, address: str) -> bool:
        """
        Check if an address is contained in this network.

        Args:
            address: IPv6 address string

        Returns:
            True if address is in network
        """
        try:
            addr = ipaddress.IPv6Address(address.split('%')[0])  # Remove zone ID
            return addr in self._network
        except (ipaddress.AddressValueError, ValueError):
            return False

    def overlaps(self, other: 'IPv6Network') -> bool:
        """
        Check if this network overlaps with another.

        Args:
            other: Another IPv6Network

        Returns:
            True if networks overlap
        """
        return self._network.overlaps(other._network)

    def __str__(self) -> str:
        """String representation."""
        return str(self._network)

    def __repr__(self) -> str:
        """Developer representation."""
        return f"IPv6Network('{str(self)}')"

    def __contains__(self, address) -> bool:
        """Support 'in' operator."""
        if isinstance(address, IPv6Address):
            return address._addr in self._network
        elif isinstance(address, str):
            return self.contains(address)
        return False
