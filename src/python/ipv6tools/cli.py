#!/usr/bin/env python3
"""
Command-line interface for IPv6 tools.
"""

import sys
import argparse
from typing import Optional

from .address import IPv6Address, IPv6Network
from .validator import validate_ipv6, validate_ipv6_network
from .utils import (
    compress_address, expand_address, generate_link_local,
    generate_unique_local, generate_random_ipv6, reverse_pointer,
    mac_to_ipv6_link_local, calculate_subnet_mask
)
from .subnet import IPv6SubnetCalculator


def format_output(data: dict, format_type: str = "text") -> str:
    """Format output data."""
    if format_type == "json":
        import json
        return json.dumps(data, indent=2)
    else:
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"  {k}: {v}")
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


def calc_cli():
    """CLI for IPv6 calculations."""
    parser = argparse.ArgumentParser(description="IPv6 subnet calculator")
    parser.add_argument("network", help="IPv6 network in CIDR notation")
    parser.add_argument("-i", "--info", action="store_true", help="Show network info")
    parser.add_argument("-d", "--divide", type=int, metavar="N", help="Divide into N subnets")
    parser.add_argument("-p", "--prefix", type=int, metavar="LEN", help="Divide by prefix length")
    parser.add_argument("-s", "--supernet", type=int, metavar="LEN", help="Get supernet with prefix length")
    parser.add_argument("-c", "--contains", metavar="ADDR", help="Check if address is in network")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    try:
        calc = IPv6SubnetCalculator(args.network)

        if args.info or (not args.divide and not args.prefix and not args.supernet and not args.contains):
            info = calc.get_info()
            output = {
                "Network": info.network,
                "Network Address": info.network_address,
                "First Address": info.first_address,
                "Last Address": info.last_address,
                "Prefix Length": info.prefix_length,
                "Number of Addresses": str(info.num_addresses),
                "Netmask": info.netmask,
            }
            print(format_output(output, args.format))

        if args.divide:
            subnets = calc.divide_into_subnets(args.divide)
            output = {"Subnets": []}
            for i, subnet in enumerate(subnets, 1):
                output["Subnets"].append({
                    f"Subnet {i}": subnet.network,
                    "Addresses": str(subnet.num_addresses),
                })
            print(format_output(output, args.format))

        if args.prefix:
            subnets = calc.divide_by_prefix(args.prefix)
            print(f"Created {len(subnets)} subnets with /{args.prefix}:")
            for subnet in subnets[:10]:  # Show first 10
                print(f"  {subnet.network}")
            if len(subnets) > 10:
                print(f"  ... and {len(subnets) - 10} more")

        if args.supernet:
            supernet = calc.get_supernet(args.supernet)
            output = {
                "Supernet": supernet.network,
                "Network Address": supernet.network_address,
                "Prefix Length": supernet.prefix_length,
            }
            print(format_output(output, args.format))

        if args.contains:
            contains = calc.contains_address(args.contains)
            print(f"{args.contains} is {'in' if contains else 'not in'} {args.network}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def validate_cli():
    """CLI for IPv6 validation."""
    parser = argparse.ArgumentParser(description="Validate IPv6 addresses and networks")
    parser.add_argument("input", nargs="+", help="IPv6 addresses or networks to validate")
    parser.add_argument("-n", "--network", action="store_true", help="Validate as network")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (exit code only)")
    parser.add_argument("--no-zone", action="store_true", help="Disallow zone IDs")

    args = parser.parse_args()

    all_valid = True

    for addr in args.input:
        if args.network:
            valid, error = validate_ipv6_network(addr)
        else:
            valid, error = validate_ipv6(addr, allow_zone=not args.no_zone)

        if not args.quiet:
            if valid:
                print(f"✓ {addr} is valid")
            else:
                print(f"✗ {addr} is invalid: {error}")
                all_valid = False
        elif not valid:
            all_valid = False

    sys.exit(0 if all_valid else 1)


def generate_cli():
    """CLI for generating IPv6 addresses."""
    parser = argparse.ArgumentParser(description="Generate IPv6 addresses")
    subparsers = parser.add_subparsers(dest="command", help="Generation type")

    # Link-local
    ll_parser = subparsers.add_parser("link-local", help="Generate link-local address")
    ll_parser.add_argument("-i", "--interface-id", help="Interface ID (64 bits hex)")

    # Unique local
    ula_parser = subparsers.add_parser("ula", help="Generate unique local address")
    ula_parser.add_argument("-g", "--global-id", help="Global ID (40 bits hex)")
    ula_parser.add_argument("-s", "--subnet-id", help="Subnet ID (16 bits hex)")
    ula_parser.add_argument("-i", "--interface-id", help="Interface ID (64 bits hex)")

    # Random
    random_parser = subparsers.add_parser("random", help="Generate random address")
    random_parser.add_argument("-p", "--prefix", default="2001:db8::/64", help="Prefix to use")

    # From MAC
    mac_parser = subparsers.add_parser("from-mac", help="Generate from MAC address")
    mac_parser.add_argument("mac", help="MAC address")

    # Generate multiple
    parser.add_argument("-n", "--count", type=int, default=1, help="Number of addresses to generate")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        for _ in range(args.count):
            if args.command == "link-local":
                addr = generate_link_local(args.interface_id)
            elif args.command == "ula":
                addr = generate_unique_local(args.global_id, args.subnet_id, args.interface_id)
            elif args.command == "random":
                addr = generate_random_ipv6(args.prefix)
            elif args.command == "from-mac":
                addr = mac_to_ipv6_link_local(args.mac)
            else:
                parser.print_help()
                sys.exit(1)

            print(addr)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def convert_cli():
    """CLI for IPv6 address conversion."""
    parser = argparse.ArgumentParser(description="Convert IPv6 addresses")
    parser.add_argument("address", help="IPv6 address to convert")
    parser.add_argument("-c", "--compress", action="store_true", help="Compress address")
    parser.add_argument("-e", "--expand", action="store_true", help="Expand address")
    parser.add_argument("-r", "--reverse", action="store_true", help="Generate reverse DNS")
    parser.add_argument("-b", "--binary", action="store_true", help="Show binary representation")
    parser.add_argument("-x", "--hex", action="store_true", help="Show hex representation")
    parser.add_argument("-a", "--all", action="store_true", help="Show all formats")

    args = parser.parse_args()

    try:
        addr = IPv6Address(args.address.split('%')[0])

        if args.all:
            print(f"Compressed:  {compress_address(args.address)}")
            print(f"Expanded:    {expand_address(args.address)}")
            print(f"Binary:      {addr.to_binary()}")
            print(f"Hexadecimal: {addr.to_hex()}")
            print(f"Reverse DNS: {reverse_pointer(args.address)}")
            print(f"Type:        {addr.get_address_type()}")
        else:
            if args.compress:
                print(compress_address(args.address))
            if args.expand:
                print(expand_address(args.address))
            if args.reverse:
                print(reverse_pointer(args.address))
            if args.binary:
                print(addr.to_binary())
            if args.hex:
                print(addr.to_hex())

            if not (args.compress or args.expand or args.reverse or args.binary or args.hex):
                # Default: show compressed
                print(compress_address(args.address))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Determine which CLI to run based on script name
    import os
    script_name = os.path.basename(sys.argv[0])

    if "calc" in script_name:
        calc_cli()
    elif "validate" in script_name:
        validate_cli()
    elif "gen" in script_name:
        generate_cli()
    elif "convert" in script_name:
        convert_cli()
    else:
        print("Unknown command. Available commands: calc, validate, generate, convert")
        sys.exit(1)
