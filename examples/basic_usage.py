#!/usr/bin/env python3
"""
Basic usage examples for IPv6 tools library.
"""

from ipv6tools import (
    IPv6Address,
    IPv6Network,
    IPv6SubnetCalculator,
    validate_ipv6,
    compress_address,
    expand_address,
    generate_link_local,
    generate_unique_local,
    mac_to_ipv6_link_local,
)


def address_examples():
    """Examples of address manipulation."""
    print("=== Address Examples ===\n")

    # Create address
    addr = IPv6Address("2001:db8::1")
    print(f"Address: {addr}")
    print(f"Compressed: {addr.compressed}")
    print(f"Expanded: {addr.exploded}")
    print(f"Type: {addr.get_address_type()}")
    print(f"Is global: {addr.is_global}")
    print()

    # Link-local address
    ll_addr = IPv6Address("fe80::1")
    print(f"Link-local: {ll_addr}")
    print(f"Is link-local: {ll_addr.is_link_local}")
    print()


def validation_examples():
    """Examples of address validation."""
    print("=== Validation Examples ===\n")

    addresses = [
        "2001:db8::1",
        "fe80::1%eth0",
        "::1",
        "invalid",
        "192.168.1.1",
    ]

    for addr in addresses:
        valid, error = validate_ipv6(addr)
        if valid:
            print(f"✓ {addr} is valid")
        else:
            print(f"✗ {addr} is invalid: {error}")
    print()


def network_examples():
    """Examples of network operations."""
    print("=== Network Examples ===\n")

    # Create network
    net = IPv6Network("2001:db8::/32")
    print(f"Network: {net}")
    print(f"Network address: {net.network_address}")
    print(f"Prefix length: {net.prefix_length}")
    print(f"Number of addresses: {net.num_addresses}")
    print()

    # Test if address is in network
    test_addrs = ["2001:db8::1", "2001:db8:1234::1", "2001:db9::1"]
    for addr in test_addrs:
        print(f"{addr} in network: {net.contains(addr)}")
    print()


def subnet_examples():
    """Examples of subnet calculations."""
    print("=== Subnet Examples ===\n")

    # Create calculator
    calc = IPv6SubnetCalculator("2001:db8::/32")

    # Get network info
    info = calc.get_info()
    print(f"Network: {info.network}")
    print(f"Prefix: /{info.prefix_length}")
    print()

    # Divide into subnets
    print("Dividing into 4 subnets:")
    subnets = calc.divide_into_subnets(4)
    for i, subnet in enumerate(subnets, 1):
        print(f"  {i}. {subnet.network}")
    print()

    # Divide by prefix
    print("Creating /34 subnets:")
    subnets = calc.divide_by_prefix(34)
    for subnet in subnets[:3]:
        print(f"  {subnet.network}")
    print(f"  ... (total {len(subnets)} subnets)")
    print()


def generation_examples():
    """Examples of address generation."""
    print("=== Address Generation Examples ===\n")

    # Generate link-local
    ll = generate_link_local()
    print(f"Random link-local: {ll}")

    # Generate with specific interface ID
    ll_custom = generate_link_local("0000000000000001")
    print(f"Link-local with custom ID: {ll_custom}")
    print()

    # Generate ULA
    ula = generate_unique_local()
    print(f"Random ULA: {ula}")
    print()

    # MAC to IPv6
    mac = "00:11:22:33:44:55"
    ipv6 = mac_to_ipv6_link_local(mac)
    print(f"MAC {mac} → IPv6: {ipv6}")
    print()


def compression_examples():
    """Examples of compression and expansion."""
    print("=== Compression/Expansion Examples ===\n")

    addresses = [
        "2001:0db8:0000:0000:0000:0000:0000:0001",
        "fe80:0000:0000:0000:0000:0000:0000:0001",
        "2001:db8:85a3:0000:0000:8a2e:0370:7334",
    ]

    for addr in addresses:
        compressed = compress_address(addr)
        expanded = expand_address(compressed)
        print(f"Original:   {addr}")
        print(f"Compressed: {compressed}")
        print(f"Expanded:   {expanded}")
        print()


def practical_example():
    """Practical example: Network planning."""
    print("=== Practical Example: Network Planning ===\n")

    # You have a /48 prefix and need to allocate subnets for departments
    base_network = "2001:db8:1234::/48"

    departments = {
        "Engineering": 16,
        "Sales": 4,
        "Marketing": 2,
        "IT": 8,
    }

    print(f"Base network: {base_network}")
    print(f"\nDepartment requirements:")
    for dept, count in departments.items():
        print(f"  {dept}: {count} subnets")

    allocation = IPv6SubnetCalculator.recommend_allocation(
        base_network, departments
    )

    print(f"\nAllocated subnets:")
    for dept, subnets in allocation.items():
        print(f"\n{dept} ({len(subnets)} subnets):")
        for subnet in subnets[:3]:  # Show first 3
            print(f"  {subnet.network}")
        if len(subnets) > 3:
            print(f"  ... and {len(subnets) - 3} more")


if __name__ == "__main__":
    address_examples()
    validation_examples()
    network_examples()
    subnet_examples()
    generation_examples()
    compression_examples()
    practical_example()

    print("\n" + "="*50)
    print("Examples complete! See the library documentation for more.")
