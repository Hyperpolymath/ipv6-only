"""
IPv6 Tools - A comprehensive library for IPv6 address manipulation and network utilities.

This library provides tools for:
- IPv6 address validation and parsing
- Address compression and expansion
- Subnet calculations
- Network operations
- IPv6-specific utilities
- DNS operations (AAAA records)
- Security scanning
- Performance benchmarking
- Network simulation
"""

__version__ = "0.1.0"
__author__ = "IPv6-Only Project"

from .address import IPv6Address, IPv6Network
from .validator import validate_ipv6, is_valid_ipv6
from .utils import (
    compress_address, expand_address, generate_link_local,
    generate_unique_local, mac_to_ipv6_link_local
)
from .subnet import IPv6SubnetCalculator

# Optional imports (may have additional dependencies)
try:
    from .dns import IPv6DNSTools
except ImportError:
    IPv6DNSTools = None

try:
    from .security import IPv6SecurityScanner
except ImportError:
    IPv6SecurityScanner = None

try:
    from .benchmark import IPv6Benchmark
except ImportError:
    IPv6Benchmark = None

try:
    from .simulator import IPv6NetworkSimulator
except ImportError:
    IPv6NetworkSimulator = None

__all__ = [
    # Core classes
    'IPv6Address',
    'IPv6Network',
    'IPv6SubnetCalculator',

    # Validation
    'validate_ipv6',
    'is_valid_ipv6',

    # Utilities
    'compress_address',
    'expand_address',
    'generate_link_local',
    'generate_unique_local',
    'mac_to_ipv6_link_local',

    # Advanced tools (if available)
    'IPv6DNSTools',
    'IPv6SecurityScanner',
    'IPv6Benchmark',
    'IPv6NetworkSimulator',
]
