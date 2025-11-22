#!/usr/bin/env python3
"""
Example: IPv6 DNS operations and analysis.

Demonstrates using IPv6 DNS tools for various operations.
"""

import sys
sys.path.insert(0, '../src/python')

from ipv6tools.dns import IPv6DNSTools


def analyze_website(hostname: str):
    """
    Analyze a website's IPv6 support.

    Args:
        hostname: Website hostname to analyze
    """
    print(f"\n{'='*80}")
    print(f"IPv6 ANALYSIS: {hostname}")
    print(f"{'='*80}\n")

    dns = IPv6DNSTools()

    # Check dual-stack support
    comparison = dns.compare_dual_stack(hostname)

    print(f"Hostname: {comparison['hostname']}")
    print(f"IPv4 Support: {'✓ Yes' if comparison['has_ipv4'] else '✗ No'}")
    print(f"IPv6 Support: {'✓ Yes' if comparison['has_ipv6'] else '✗ No'}")

    if comparison['is_dual_stack']:
        print(f"Type: 🟢 Dual-Stack (Full IPv6 support)")
    elif comparison['is_ipv6_only']:
        print(f"Type: 🔵 IPv6-Only")
    elif comparison['is_ipv4_only']:
        print(f"Type: 🟡 IPv4-Only (No IPv6 support)")

    # Show addresses
    if comparison['ipv4_addresses']:
        print(f"\nIPv4 Addresses:")
        for addr in comparison['ipv4_addresses']:
            print(f"  {addr}")

    if comparison['ipv6_addresses']:
        print(f"\nIPv6 Addresses:")
        for addr in comparison['ipv6_addresses']:
            print(f"  {addr}")

    # Test connectivity
    if comparison['has_ipv6']:
        print(f"\nTesting IPv6 connectivity...")
        success, address = dns.test_connectivity(hostname, 80, timeout=3.0)

        if success:
            print(f"  ✓ Successfully connected via {address}")

            # Try reverse lookup
            ptr = dns.reverse_lookup(address)
            if ptr:
                print(f"  Reverse DNS: {ptr}")
        else:
            print(f"  ✗ Could not connect (port 80 may be closed)")

    print()


def batch_analysis(hostnames: list):
    """
    Analyze multiple websites.

    Args:
        hostnames: List of hostnames to analyze
    """
    print("\n" + "="*80)
    print("BATCH IPv6 SUPPORT ANALYSIS")
    print("="*80 + "\n")

    dns = IPv6DNSTools()

    # Batch lookup
    results = dns.batch_lookup(hostnames)

    # Create summary
    summary = {
        'dual_stack': 0,
        'ipv6_only': 0,
        'ipv4_only': 0,
        'error': 0
    }

    print(f"{'Hostname':<30s} {'IPv4':^10s} {'IPv6':^10s} {'Type':^15s}")
    print("-"*80)

    for hostname, data in results.items():
        if 'error' in data:
            ipv4_status = "Error"
            ipv6_status = "Error"
            type_str = "Error"
            summary['error'] += 1
        else:
            ipv4_status = "✓" if data['ipv4'] else "✗"
            ipv6_status = "✓" if data['ipv6'] else "✗"

            if data['ipv4'] and data['ipv6']:
                type_str = "Dual-Stack"
                summary['dual_stack'] += 1
            elif data['ipv6']:
                type_str = "IPv6-Only"
                summary['ipv6_only'] += 1
            elif data['ipv4']:
                type_str = "IPv4-Only"
                summary['ipv4_only'] += 1
            else:
                type_str = "Unknown"

        print(f"{hostname:<30s} {ipv4_status:^10s} {ipv6_status:^10s} {type_str:^15s}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    total = len(hostnames)
    print(f"Total analyzed: {total}")
    print(f"Dual-Stack: {summary['dual_stack']} ({summary['dual_stack']/total*100:.1f}%)")
    print(f"IPv6-Only: {summary['ipv6_only']} ({summary['ipv6_only']/total*100:.1f}%)")
    print(f"IPv4-Only: {summary['ipv4_only']} ({summary['ipv4_only']/total*100:.1f}%)")
    if summary['error'] > 0:
        print(f"Errors: {summary['error']}")

    print()


def demonstrate_dns_operations():
    """Demonstrate various DNS operations."""

    print("="*80)
    print("IPv6 DNS OPERATIONS DEMONSTRATION")
    print("="*80)

    dns = IPv6DNSTools()

    # Example hostnames that typically have IPv6
    examples = [
        "google.com",
        "facebook.com",
        "cloudflare.com",
    ]

    print("\nNote: This example demonstrates DNS operations.")
    print("Results depend on your network connectivity and DNS configuration.\n")

    # Analyze each
    for hostname in examples:
        try:
            analyze_website(hostname)
        except Exception as e:
            print(f"Error analyzing {hostname}: {e}\n")

    # Batch analysis
    print("\n" + "="*80)
    print("Running batch analysis...")
    print("="*80)

    batch_hostnames = examples + [
        "microsoft.com",
        "apple.com",
        "amazon.com",
    ]

    batch_analysis(batch_hostnames)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IPv6 DNS Operations Example")
    parser.add_argument("hostname", nargs="?", help="Hostname to analyze")
    parser.add_argument("-b", "--batch", nargs="+", help="Multiple hostnames")

    args = parser.parse_args()

    if args.batch:
        # Batch mode
        batch_analysis(args.batch)
    elif args.hostname:
        # Single hostname
        analyze_website(args.hostname)
    else:
        # Demo mode
        demonstrate_dns_operations()
