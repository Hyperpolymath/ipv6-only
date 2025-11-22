"""
IPv6 Tools - A comprehensive library for IPv6 address manipulation and network utilities.

This library provides tools for:
- IPv6 address validation and parsing
- Address compression and expansion
- Subnet calculations
- Network operations
- IPv6-specific utilities
"""

__version__ = "0.1.0"
__author__ = "IPv6-Only Project"

from .address import IPv6Address, IPv6Network
from .validator import validate_ipv6, is_valid_ipv6
from .utils import compress_address, expand_address, generate_link_local, generate_unique_local
from .subnet import IPv6SubnetCalculator

__all__ = [
    'IPv6Address',
    'IPv6Network',
    'validate_ipv6',
    'is_valid_ipv6',
    'compress_address',
    'expand_address',
    'generate_link_local',
    'generate_unique_local',
    'IPv6SubnetCalculator',
]
