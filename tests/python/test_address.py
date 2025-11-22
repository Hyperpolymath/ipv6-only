"""
Tests for IPv6 address module.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/python'))

from ipv6tools.address import IPv6Address, IPv6Network


class TestIPv6Address:
    """Test IPv6Address class."""

    def test_valid_address_compressed(self):
        """Test creating address from compressed format."""
        addr = IPv6Address("2001:db8::1")
        assert addr.compressed == "2001:db8::1"
        assert addr.exploded == "2001:0db8:0000:0000:0000:0000:0000:0001"

    def test_valid_address_expanded(self):
        """Test creating address from expanded format."""
        addr = IPv6Address("2001:0db8:0000:0000:0000:0000:0000:0001")
        assert addr.compressed == "2001:db8::1"
        assert addr.exploded == "2001:0db8:0000:0000:0000:0000:0000:0001"

    def test_loopback_address(self):
        """Test loopback address."""
        addr = IPv6Address("::1")
        assert addr.is_loopback
        assert addr.get_address_type() == "Loopback"

    def test_link_local_address(self):
        """Test link-local address."""
        addr = IPv6Address("fe80::1")
        assert addr.is_link_local
        assert addr.get_address_type() == "Link-Local"

    def test_unique_local_address(self):
        """Test unique local address."""
        addr = IPv6Address("fd00::1")
        assert addr.is_private
        assert addr.get_address_type() == "Unique Local (ULA)"

    def test_multicast_address(self):
        """Test multicast address."""
        addr = IPv6Address("ff02::1")
        assert addr.is_multicast
        assert addr.get_address_type() == "Multicast"

    def test_global_address(self):
        """Test global unicast address."""
        addr = IPv6Address("2001:db8::1")
        assert addr.is_global
        assert addr.get_address_type() == "Global Unicast"

    def test_unspecified_address(self):
        """Test unspecified address."""
        addr = IPv6Address("::")
        assert addr.is_unspecified
        assert addr.get_address_type() == "Unspecified"

    def test_zone_id(self):
        """Test address with zone ID."""
        addr = IPv6Address("fe80::1%eth0")
        assert addr.compressed == "fe80::1"
        assert addr.zone_id == "eth0"
        assert str(addr) == "fe80::1%eth0"

    def test_to_binary(self):
        """Test binary conversion."""
        addr = IPv6Address("::1")
        binary = addr.to_binary()
        assert len(binary) == 128
        assert binary == "0" * 127 + "1"

    def test_to_hex(self):
        """Test hex conversion."""
        addr = IPv6Address("2001:db8::1")
        hex_str = addr.to_hex()
        assert len(hex_str) == 32

    def test_equality(self):
        """Test address equality."""
        addr1 = IPv6Address("2001:db8::1")
        addr2 = IPv6Address("2001:0db8::1")
        addr3 = IPv6Address("2001:db8::2")
        assert addr1 == addr2
        assert addr1 != addr3

    def test_invalid_address(self):
        """Test invalid address raises error."""
        with pytest.raises(ValueError):
            IPv6Address("invalid")

        with pytest.raises(ValueError):
            IPv6Address("192.168.1.1")  # IPv4


class TestIPv6Network:
    """Test IPv6Network class."""

    def test_valid_network(self):
        """Test creating valid network."""
        net = IPv6Network("2001:db8::/32")
        assert net.prefix_length == 32
        assert str(net) == "2001:db8::/32"

    def test_network_properties(self):
        """Test network properties."""
        net = IPv6Network("2001:db8::/32")
        assert net.network_address.compressed == "2001:db8::"
        assert net.prefix_length == 32
        assert net.netmask == "ffff:ffff::"

    def test_contains_address(self):
        """Test checking if address is in network."""
        net = IPv6Network("2001:db8::/32")
        assert net.contains("2001:db8::1")
        assert net.contains("2001:db8:1234:5678::1")
        assert not net.contains("2001:db9::1")

    def test_contains_operator(self):
        """Test 'in' operator."""
        net = IPv6Network("2001:db8::/32")
        addr = IPv6Address("2001:db8::1")
        assert addr in net
        assert "2001:db8::1" in net

    def test_subnet_division(self):
        """Test dividing network into subnets."""
        net = IPv6Network("2001:db8::/32")
        subnets = net.subnets(prefixlen_diff=1)
        assert len(subnets) == 2
        assert subnets[0].prefix_length == 33
        assert subnets[1].prefix_length == 33

    def test_supernet(self):
        """Test getting supernet."""
        net = IPv6Network("2001:db8::/32")
        supernet = net.supernet(prefixlen_diff=1)
        assert supernet.prefix_length == 31

    def test_overlaps(self):
        """Test network overlap detection."""
        net1 = IPv6Network("2001:db8::/32")
        net2 = IPv6Network("2001:db8:1::/48")
        net3 = IPv6Network("2001:db9::/32")

        assert net1.overlaps(net2)
        assert not net1.overlaps(net3)

    def test_num_addresses(self):
        """Test address count."""
        net = IPv6Network("2001:db8::/126")
        assert net.num_addresses == 4

    def test_hosts_small_network(self):
        """Test enumerating hosts in small network."""
        net = IPv6Network("2001:db8::/126")
        # Note: hosts() excludes network and broadcast addresses
        # But IPv6 doesn't have broadcast, so it just excludes first and last

    def test_hosts_large_network_raises(self):
        """Test that enumerating large network raises error."""
        net = IPv6Network("2001:db8::/32")
        with pytest.raises(ValueError):
            net.hosts()

    def test_invalid_network(self):
        """Test invalid network raises error."""
        with pytest.raises(ValueError):
            IPv6Network("invalid")

        with pytest.raises(ValueError):
            IPv6Network("2001:db8::")  # Missing prefix

    def test_strict_mode(self):
        """Test strict mode validation."""
        # Non-strict allows host bits set
        net1 = IPv6Network("2001:db8::1/32", strict=False)
        assert str(net1) == "2001:db8::/32"

        # Strict raises error if host bits set
        with pytest.raises(ValueError):
            IPv6Network("2001:db8::1/32", strict=True)
