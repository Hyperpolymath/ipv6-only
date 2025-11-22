"""
IPv6 utility functions for address manipulation and generation.
"""

import ipaddress
import secrets
from typing import Optional


def compress_address(address: str) -> str:
    """
    Compress an IPv6 address to its shortest form.

    Args:
        address: IPv6 address in any valid format

    Returns:
        Compressed IPv6 address

    Raises:
        ValueError: If address is invalid
    """
    zone_id = None
    if '%' in address:
        address, zone_id = address.split('%', 1)

    try:
        addr = ipaddress.IPv6Address(address)
        compressed = addr.compressed
        if zone_id:
            compressed += f"%{zone_id}"
        return compressed
    except ipaddress.AddressValueError as e:
        raise ValueError(f"Invalid IPv6 address: {e}")


def expand_address(address: str) -> str:
    """
    Expand an IPv6 address to its full form.

    Args:
        address: IPv6 address in any valid format

    Returns:
        Fully expanded IPv6 address

    Raises:
        ValueError: If address is invalid
    """
    zone_id = None
    if '%' in address:
        address, zone_id = address.split('%', 1)

    try:
        addr = ipaddress.IPv6Address(address)
        expanded = addr.exploded
        if zone_id:
            expanded += f"%{zone_id}"
        return expanded
    except ipaddress.AddressValueError as e:
        raise ValueError(f"Invalid IPv6 address: {e}")


def generate_link_local(interface_id: Optional[str] = None) -> str:
    """
    Generate an IPv6 link-local address (fe80::/10).

    Args:
        interface_id: Optional interface identifier (64 bits in hex)
                     If not provided, a random one is generated

    Returns:
        Link-local IPv6 address
    """
    if interface_id is None:
        # Generate random 64-bit interface ID
        interface_id = secrets.token_hex(8)

    # Ensure interface_id is 16 hex characters (64 bits)
    interface_id = interface_id.replace(':', '').replace('-', '')
    if len(interface_id) != 16:
        raise ValueError("Interface ID must be 64 bits (16 hex characters)")

    # Format as IPv6 address: fe80::xxxx:xxxx:xxxx:xxxx
    parts = [interface_id[i:i+4] for i in range(0, 16, 4)]
    address = f"fe80::{parts[0]}:{parts[1]}:{parts[2]}:{parts[3]}"

    return compress_address(address)


def generate_unique_local(global_id: Optional[str] = None, subnet_id: Optional[str] = None,
                         interface_id: Optional[str] = None) -> str:
    """
    Generate a Unique Local Address (ULA) in the fc00::/7 range.

    Args:
        global_id: Optional 40-bit global ID (10 hex chars)
        subnet_id: Optional 16-bit subnet ID (4 hex chars)
        interface_id: Optional 64-bit interface ID (16 hex chars)

    Returns:
        Unique Local IPv6 address
    """
    # Generate random values if not provided
    if global_id is None:
        global_id = secrets.token_hex(5)  # 40 bits

    if subnet_id is None:
        subnet_id = secrets.token_hex(2)  # 16 bits

    if interface_id is None:
        interface_id = secrets.token_hex(8)  # 64 bits

    # Clean up input
    global_id = global_id.replace(':', '').replace('-', '')
    subnet_id = subnet_id.replace(':', '').replace('-', '')
    interface_id = interface_id.replace(':', '').replace('-', '')

    # Validate lengths
    if len(global_id) != 10:
        raise ValueError("Global ID must be 40 bits (10 hex characters)")
    if len(subnet_id) != 4:
        raise ValueError("Subnet ID must be 16 bits (4 hex characters)")
    if len(interface_id) != 16:
        raise ValueError("Interface ID must be 64 bits (16 hex characters)")

    # Construct ULA: fd00::/8 + 40-bit global ID + 16-bit subnet + 64-bit interface
    # Using fd prefix (locally assigned)
    prefix = "fd"
    global_parts = [global_id[i:i+4] for i in range(0, 10, 4)]
    interface_parts = [interface_id[i:i+4] for i in range(0, 16, 4)]

    # Combine parts
    address = f"{prefix}{global_id[:2]}:{global_parts[1]}:{global_parts[2]}{subnet_id}:"
    address += f"{interface_parts[0]}:{interface_parts[1]}:{interface_parts[2]}:{interface_parts[3]}"

    return compress_address(address)


def generate_random_ipv6(prefix: str = "2001:db8::") -> str:
    """
    Generate a random IPv6 address with given prefix.

    Args:
        prefix: IPv6 prefix (default is documentation prefix)

    Returns:
        Random IPv6 address
    """
    # Parse the network
    if '/' not in prefix:
        prefix += "/64"  # Default to /64

    network = ipaddress.IPv6Network(prefix, strict=False)
    prefix_len = network.prefixlen

    # Calculate how many random bits we need
    host_bits = 128 - prefix_len
    random_bytes = (host_bits + 7) // 8

    # Generate random host part
    random_int = int.from_bytes(secrets.token_bytes(random_bytes), byteorder='big')
    random_int &= (1 << host_bits) - 1  # Mask to host bits

    # Combine with network address
    network_int = int(network.network_address)
    address_int = network_int | random_int

    # Convert to IPv6 address
    address = ipaddress.IPv6Address(address_int)
    return address.compressed


def reverse_pointer(address: str) -> str:
    """
    Generate reverse DNS pointer (PTR) record name for IPv6 address.

    Args:
        address: IPv6 address

    Returns:
        Reverse DNS name (e.g., "1.0.0.0...ip6.arpa")
    """
    # Remove zone ID if present
    if '%' in address:
        address = address.split('%')[0]

    addr = ipaddress.IPv6Address(address)
    # Get fully expanded address without colons
    exploded = addr.exploded.replace(':', '')

    # Reverse and add dots between each character
    reversed_nibbles = '.'.join(reversed(exploded))

    return f"{reversed_nibbles}.ip6.arpa"


def mac_to_ipv6_link_local(mac: str) -> str:
    """
    Convert MAC address to IPv6 link-local address using EUI-64.

    Args:
        mac: MAC address (various formats supported)

    Returns:
        IPv6 link-local address

    Raises:
        ValueError: If MAC address is invalid
    """
    # Clean MAC address
    mac = mac.replace(':', '').replace('-', '').replace('.', '').lower()

    if len(mac) != 12:
        raise ValueError("Invalid MAC address length")

    # Validate hex
    try:
        int(mac, 16)
    except ValueError:
        raise ValueError("Invalid MAC address format")

    # Convert to EUI-64
    # Insert FFFE in the middle
    eui64 = mac[:6] + 'fffe' + mac[6:]

    # Flip the universal/local bit (7th bit of first octet)
    first_octet = int(eui64[:2], 16)
    first_octet ^= 0x02  # Flip bit
    eui64 = f"{first_octet:02x}" + eui64[2:]

    # Format as IPv6 link-local address
    parts = [eui64[i:i+4] for i in range(0, 16, 4)]
    address = f"fe80::{parts[0]}:{parts[1]}:{parts[2]}:{parts[3]}"

    return compress_address(address)


def calculate_subnet_mask(prefix_length: int) -> str:
    """
    Calculate the subnet mask for a given prefix length.

    Args:
        prefix_length: Prefix length (0-128)

    Returns:
        IPv6 subnet mask

    Raises:
        ValueError: If prefix length is invalid
    """
    if not 0 <= prefix_length <= 128:
        raise ValueError("Prefix length must be between 0 and 128")

    # Create network with prefix
    network = ipaddress.IPv6Network(f"::/{prefix_length}")
    return str(network.netmask)
