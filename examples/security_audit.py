#!/usr/bin/env python3
"""
Example: IPv6 security audit of network hosts.

This demonstrates using the security scanner to audit a network
and generate a security report.
"""

import sys
sys.path.insert(0, '../src/python')

from ipv6tools.security import IPv6SecurityScanner
from ipv6tools.dns import IPv6DNSTools


def audit_host(address: str):
    """
    Perform security audit on a single host.

    Args:
        address: IPv6 address or hostname to audit
    """
    print(f"\n{'='*80}")
    print(f"SECURITY AUDIT: {address}")
    print(f"{'='*80}\n")

    scanner = IPv6SecurityScanner(timeout=2.0, max_workers=50)

    # Resolve hostname if needed
    actual_address = address
    if not address.startswith('2') and not address.startswith('fe80'):
        dns = IPv6DNSTools()
        try:
            addresses = dns.lookup_aaaa(address)
            if addresses:
                actual_address = addresses[0]
                print(f"Resolved {address} to {actual_address}\n")
        except:
            print(f"Could not resolve {address}\n")
            return

    # Run security audit
    print("Running security audit...")
    result = scanner.security_audit(actual_address)

    # Print results
    print(f"\nOpen Ports: {len(result.open_ports)}")
    if result.open_ports:
        for port in result.open_ports[:10]:  # Show first 10
            service = scanner._get_service_name(port)
            print(f"  {port:5d} - {service}")
        if len(result.open_ports) > 10:
            print(f"  ... and {len(result.open_ports) - 10} more")

    # Vulnerabilities
    if result.vulnerabilities:
        print(f"\n❌ VULNERABILITIES FOUND: {len(result.vulnerabilities)}")
        for vuln in result.vulnerabilities:
            print(f"   {vuln}")

    # Warnings
    if result.warnings:
        print(f"\n⚠️  WARNINGS: {len(result.warnings)}")
        for warn in result.warnings:
            print(f"   {warn}")

    # Additional information
    if result.info:
        print(f"\nℹ️  INFORMATION:")
        for key, value in result.info.items():
            print(f"   {key}: {value}")

    # IPv6-specific checks
    ipv6_issues = scanner.check_ipv6_specific_issues(actual_address)
    if ipv6_issues:
        print(f"\n⚠️  IPv6-SPECIFIC ISSUES:")
        for issue in ipv6_issues:
            print(f"   {issue}")

    # Privacy check
    privacy = scanner.privacy_check(actual_address)
    print(f"\n🔒 PRIVACY ANALYSIS:")
    print(f"   Interface ID: {privacy['interface_id']}")
    print(f"   Likely EUI-64: {privacy['likely_eui64']}")
    print(f"   Privacy Extensions: {privacy['likely_privacy_extension']}")
    print(f"   Recommendation: {privacy['recommendation']}")

    # Risk assessment
    risk_score = 0
    if result.vulnerabilities:
        risk_score += len(result.vulnerabilities) * 10
    if result.warnings:
        risk_score += len(result.warnings) * 5
    if len(result.open_ports) > 5:
        risk_score += 10

    print(f"\n📊 RISK ASSESSMENT: ", end='')
    if risk_score > 30:
        print("🔴 HIGH")
    elif risk_score > 15:
        print("🟡 MEDIUM")
    else:
        print("🟢 LOW")

    print()


def audit_network_hosts():
    """Audit common network infrastructure."""

    print("="*80)
    print("NETWORK INFRASTRUCTURE SECURITY AUDIT")
    print("="*80)

    # Common infrastructure hosts
    hosts = [
        ("DNS Resolver", "2001:4860:4860::8888"),  # Google DNS
        ("DNS Resolver", "2606:4700:4700::1111"),  # Cloudflare DNS
    ]

    for name, address in hosts:
        print(f"\nAuditing {name} ({address})...")

        scanner = IPv6SecurityScanner(timeout=1.0)
        result = scanner.quick_scan(address)

        if result:
            print(f"  Open ports: {', '.join(str(r.port) for r in result)}")
        else:
            print(f"  No open ports found (or host unreachable)")


def generate_compliance_report():
    """Generate compliance report for security audit."""

    print("\n" + "="*80)
    print("IPv6 SECURITY COMPLIANCE CHECKLIST")
    print("="*80 + "\n")

    checklist = [
        ("ICMPv6 properly configured", "Must allow ICMPv6 for NDP"),
        ("Privacy extensions enabled", "Recommended for client devices"),
        ("Firewall configured for IPv6", "Same rigor as IPv4"),
        ("No unnecessary services", "Close unused ports"),
        ("Secure protocols only", "Disable Telnet, use SSH"),
        ("Router advertisements secured", "Prevent rogue RAs"),
        ("Neighbor discovery protected", "ND spoofing prevention"),
        ("Extension headers filtered", "Block unnecessary headers"),
        ("Reverse DNS configured", "PTR records for servers"),
        ("Monitoring in place", "Log IPv6 traffic"),
    ]

    for i, (item, note) in enumerate(checklist, 1):
        print(f"{i:2d}. [ ] {item:35s} - {note}")

    print("\n" + "="*80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IPv6 Security Audit Example")
    parser.add_argument("target", nargs="?", help="Target to audit (address or hostname)")

    args = parser.parse_args()

    if args.target:
        # Audit specific target
        audit_host(args.target)
    else:
        # Run example audits
        print("No target specified. Running example audit...")
        print("\nNote: This example shows the audit process.")
        print("For real audits, provide a target: python security_audit.py <address>")

        # Show checklist
        generate_compliance_report()
