"""
IPv6 address validation utilities.
"""

import re
import ipaddress
from typing import Tuple, Optional


def is_valid_ipv6(address: str, allow_zone: bool = True) -> bool:
    """
    Check if a string is a valid IPv6 address.

    Args:
        address: String to validate
        allow_zone: Whether to allow zone IDs (e.g., fe80::1%eth0)

    Returns:
        True if valid IPv6 address
    """
    if not address:
        return False

    # Handle zone ID
    if '%' in address:
        if not allow_zone:
            return False
        address = address.split('%')[0]

    try:
        ipaddress.IPv6Address(address)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False


def validate_ipv6(address: str, allow_zone: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate IPv6 address with detailed error message.

    Args:
        address: String to validate
        allow_zone: Whether to allow zone IDs

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not address:
        return False, "Address cannot be empty"

    if not isinstance(address, str):
        return False, "Address must be a string"

    # Check for zone ID
    zone_id = None
    if '%' in address:
        if not allow_zone:
            return False, "Zone IDs are not allowed"
        parts = address.split('%')
        if len(parts) != 2:
            return False, "Invalid zone ID format"
        address, zone_id = parts
        if not zone_id:
            return False, "Zone ID cannot be empty"

    # Validate address format
    try:
        ipaddress.IPv6Address(address)
        return True, None
    except ipaddress.AddressValueError as e:
        return False, str(e)
    except ValueError as e:
        return False, str(e)


def is_valid_ipv6_network(network: str) -> bool:
    """
    Check if a string is a valid IPv6 network in CIDR notation.

    Args:
        network: String to validate (e.g., "2001:db8::/32")

    Returns:
        True if valid IPv6 network
    """
    if not network:
        return False

    try:
        ipaddress.IPv6Network(network, strict=False)
        return True
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
        return False


def validate_ipv6_network(network: str) -> Tuple[bool, Optional[str]]:
    """
    Validate IPv6 network with detailed error message.

    Args:
        network: String to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not network:
        return False, "Network cannot be empty"

    if not isinstance(network, str):
        return False, "Network must be a string"

    if '/' not in network:
        return False, "Network must include prefix length (e.g., 2001:db8::/32)"

    try:
        ipaddress.IPv6Network(network, strict=False)
        return True, None
    except ipaddress.AddressValueError as e:
        return False, str(e)
    except ipaddress.NetmaskValueError as e:
        return False, str(e)
    except ValueError as e:
        return False, str(e)


def is_compressed_format(address: str) -> bool:
    """
    Check if an IPv6 address is in compressed format.

    Args:
        address: IPv6 address string

    Returns:
        True if address contains :: (compressed)
    """
    return '::' in address


def is_expanded_format(address: str) -> bool:
    """
    Check if an IPv6 address is in fully expanded format.

    Args:
        address: IPv6 address string

    Returns:
        True if address is fully expanded
    """
    if not is_valid_ipv6(address):
        return False

    # Remove zone ID if present
    clean_addr = address.split('%')[0]

    # Fully expanded format has 8 groups of 4 hex digits separated by colons
    pattern = r'^[0-9a-fA-F]{4}(:[0-9a-fA-F]{4}){7}$'
    return bool(re.match(pattern, clean_addr))


def validate_prefix_length(prefix: int) -> Tuple[bool, Optional[str]]:
    """
    Validate IPv6 prefix length.

    Args:
        prefix: Prefix length (0-128)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(prefix, int):
        return False, "Prefix length must be an integer"

    if prefix < 0 or prefix > 128:
        return False, "Prefix length must be between 0 and 128"

    return True, None


def is_valid_prefix_length(prefix: int) -> bool:
    """
    Check if prefix length is valid for IPv6.

    Args:
        prefix: Prefix length to check

    Returns:
        True if valid
    """
    return isinstance(prefix, int) and 0 <= prefix <= 128
