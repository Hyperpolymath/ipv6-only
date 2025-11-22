#!/usr/bin/env python3
"""
Practical example: Enterprise IPv6 network planning.

This example demonstrates planning and allocating IPv6 address space
for an enterprise network with multiple departments and locations.
"""

from ipv6tools import IPv6Network, IPv6SubnetCalculator


def plan_enterprise_network():
    """Plan IPv6 addressing for enterprise network."""

    print("="*80)
    print("ENTERPRISE IPv6 NETWORK PLANNING")
    print("="*80)
    print()

    # Company receives a /32 from their ISP
    company_prefix = "2001:db8::/32"

    print(f"Company allocation: {company_prefix}")
    print()

    # Plan site allocations (/40 per site - 256 sites possible)
    print("SITE ALLOCATION PLAN (/40 per site)")
    print("-"*80)

    sites = {
        "HQ":         "2001:db8:0::/40",
        "DataCenter": "2001:db8:100::/40",
        "Branch1":    "2001:db8:200::/40",
        "Branch2":    "2001:db8:300::/40",
    }

    for site_name, site_prefix in sites.items():
        net = IPv6Network(site_prefix)
        print(f"{site_name:15s} {site_prefix:30s} ({net.num_addresses:,} addresses)")

    print()

    # Plan HQ network in detail
    print("HQ NETWORK DETAILS (/48 per building)")
    print("-"*80)

    hq_calc = IPv6SubnetCalculator("2001:db8:0::/40")

    # Divide into buildings (/48 each)
    buildings = {
        "Building-A": 20,  # 20 subnets needed
        "Building-B": 15,
        "Building-C": 10,
        "Building-D": 5,
    }

    total_subnets = sum(buildings.values())
    print(f"\nTotal subnets needed: {total_subnets}")

    allocation = IPv6SubnetCalculator.recommend_allocation(
        "2001:db8:0::/40",
        buildings
    )

    for building, subnets in allocation.items():
        print(f"\n{building}:")
        print(f"  Allocated subnets: {len(subnets)}")
        print(f"  First subnet: {subnets[0].network}")
        print(f"  Last subnet:  {subnets[-1].network}")

    print()

    # Plan Building-A VLANs
    print("BUILDING-A VLAN PLAN (/64 per VLAN)")
    print("-"*80)

    building_a_prefix = allocation["Building-A"][0].network

    vlans = {
        "Management":  1,
        "Servers":     2,
        "Workstations": 5,
        "Guest":       1,
        "IoT":         1,
        "Lab":         3,
    }

    vlan_calc = IPv6SubnetCalculator(building_a_prefix)
    vlan_allocation = vlan_calc.divide_into_subnets(sum(vlans.values()))

    current_subnet = 0
    for vlan_name, count in vlans.items():
        print(f"\n{vlan_name}:")
        for i in range(count):
            subnet = vlan_allocation[current_subnet]
            print(f"  VLAN {current_subnet + 1}: {subnet.network}")
            current_subnet += 1

    print()

    # Address assignment examples
    print("EXAMPLE ADDRESS ASSIGNMENTS")
    print("-"*80)

    mgmt_net = IPv6Network(vlan_allocation[0].network)
    print(f"\nManagement VLAN: {mgmt_net}")
    print(f"  Gateway:       {mgmt_net.network_address.compressed}1")
    print(f"  DNS Server 1:  {mgmt_net.network_address.compressed}10")
    print(f"  DNS Server 2:  {mgmt_net.network_address.compressed}11")
    print(f"  DHCP Server:   {mgmt_net.network_address.compressed}12")
    print(f"  NTP Server:    {mgmt_net.network_address.compressed}13")

    print()

    # Calculate statistics
    print("SUMMARY STATISTICS")
    print("-"*80)

    total_sites = len(sites)
    subnets_per_site = 256  # /40 can be divided into 256 /48s
    vlans_per_building = 65536  # /48 can be divided into 65536 /64s

    print(f"Total sites allocated:        {total_sites}")
    print(f"Remaining sites available:    {256 - total_sites}")
    print(f"Subnets per site (/48):       {subnets_per_site}")
    print(f"VLANs per building (/64):     {vlans_per_building}")
    print(f"Addresses per VLAN:           2^64 (18,446,744,073,709,551,616)")

    print()
    print("="*80)


def plan_datacenter_network():
    """Plan IPv6 addressing for data center."""

    print("\n\nDATACENTER IPv6 NETWORK PLANNING")
    print("="*80)
    print()

    dc_prefix = "2001:db8:100::/40"

    print(f"Data Center allocation: {dc_prefix}")
    print()

    # Plan racks and subnets
    print("RACK ALLOCATION PLAN")
    print("-"*80)

    zones = {
        "Web-Tier":    "2001:db8:100:0::/48",
        "App-Tier":    "2001:db8:100:1::/48",
        "DB-Tier":     "2001:db8:100:2::/48",
        "Storage":     "2001:db8:100:3::/48",
        "Management":  "2001:db8:100:ff::/48",
    }

    for zone_name, zone_prefix in zones.items():
        calc = IPv6SubnetCalculator(zone_prefix)
        info = calc.get_info()
        print(f"{zone_name:15s} {zone_prefix:30s}")

        # Calculate racks (assuming /64 per rack)
        racks = calc.divide_by_prefix(64)
        print(f"  Available racks (/64): {len(racks):,}")

    print()

    # Plan specific rack
    print("WEB TIER - RACK DETAILS")
    print("-"*80)

    web_calc = IPv6SubnetCalculator("2001:db8:100:0::/48")
    web_racks = web_calc.divide_into_subnets(16)  # 16 racks

    for i, rack in enumerate(web_racks[:4], 1):  # Show first 4
        print(f"\nRack {i}: {rack.network}")
        print(f"  Capacity: {rack.num_addresses:,} addresses")
        print(f"  Prefix: /{rack.prefix_length}")

    print()
    print("="*80)


if __name__ == "__main__":
    plan_enterprise_network()
    plan_datacenter_network()

    print("\nNetwork planning complete!")
    print("\nNext steps:")
    print("1. Document addressing plan")
    print("2. Configure routers and switches")
    print("3. Set up DNS (AAAA records)")
    print("4. Configure firewall rules")
    print("5. Test connectivity")
