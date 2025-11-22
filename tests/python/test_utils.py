"""
Tests for IPv6 utilities module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/python'))

from ipv6tools.utils import (
    compress_address,
    expand_address,
    generate_link_local,
    generate_unique_local,
    generate_random_ipv6,
    reverse_pointer,
    mac_to_ipv6_link_local,
    calculate_subnet_mask,
)


class TestAddressCompression:
    """Test address compression and expansion."""

    def test_compress_address(self):
        """Test compressing IPv6 address."""
        expanded = "2001:0db8:0000:0000:0000:0000:0000:0001"
        compressed = compress_address(expanded)
        assert compressed == "2001:db8::1"

    def test_compress_already_compressed(self):
        """Test compressing already compressed address."""
        addr = "2001:db8::1"
        compressed = compress_address(addr)
        assert compressed == "2001:db8::1"

    def test_compress_with_zone(self):
        """Test compressing address with zone ID."""
        addr = "fe80:0000:0000:0000:0000:0000:0000:0001%eth0"
        compressed = compress_address(addr)
        assert compressed == "fe80::1%eth0"

    def test_expand_address(self):
        """Test expanding IPv6 address."""
        compressed = "2001:db8::1"
        expanded = expand_address(compressed)
        assert expanded == "2001:0db8:0000:0000:0000:0000:0000:0001"

    def test_expand_already_expanded(self):
        """Test expanding already expanded address."""
        addr = "2001:0db8:0000:0000:0000:0000:0000:0001"
        expanded = expand_address(addr)
        assert expanded == "2001:0db8:0000:0000:0000:0000:0000:0001"

    def test_expand_with_zone(self):
        """Test expanding address with zone ID."""
        addr = "fe80::1%eth0"
        expanded = expand_address(addr)
        assert expanded == "fe80:0000:0000:0000:0000:0000:0000:0001%eth0"

    def test_invalid_address_compression(self):
        """Test invalid address raises error."""
        with pytest.raises(ValueError):
            compress_address("invalid")

    def test_invalid_address_expansion(self):
        """Test invalid address raises error."""
        with pytest.raises(ValueError):
            expand_address("invalid")


class TestLinkLocalGeneration:
    """Test link-local address generation."""

    def test_generate_link_local_random(self):
        """Test generating random link-local address."""
        addr = generate_link_local()
        assert addr.startswith("fe80::")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_generate_link_local_with_interface_id(self):
        """Test generating link-local with specific interface ID."""
        interface_id = "0000000000000001"
        addr = generate_link_local(interface_id)
        assert addr.startswith("fe80::")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_generate_link_local_invalid_interface_id(self):
        """Test invalid interface ID."""
        with pytest.raises(ValueError):
            generate_link_local("invalid")

        with pytest.raises(ValueError):
            generate_link_local("00:00:00:00")  # Too short


class TestUniqueLocalGeneration:
    """Test unique local address generation."""

    def test_generate_unique_local_random(self):
        """Test generating random ULA."""
        addr = generate_unique_local()
        assert addr.startswith("fd")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_generate_unique_local_with_params(self):
        """Test generating ULA with specific parameters."""
        global_id = "0123456789"
        subnet_id = "abcd"
        interface_id = "0000000000000001"

        addr = generate_unique_local(global_id, subnet_id, interface_id)
        assert addr.startswith("fd")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_generate_unique_local_invalid_params(self):
        """Test invalid parameters."""
        with pytest.raises(ValueError):
            generate_unique_local(global_id="short")

        with pytest.raises(ValueError):
            generate_unique_local(subnet_id="toolong")

        with pytest.raises(ValueError):
            generate_unique_local(interface_id="short")


class TestRandomIPv6Generation:
    """Test random IPv6 generation."""

    def test_generate_random_default(self):
        """Test generating random address with default prefix."""
        addr = generate_random_ipv6()
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_generate_random_custom_prefix(self):
        """Test generating random address with custom prefix."""
        addr = generate_random_ipv6("2001:db8::/32")
        assert addr.startswith("2001:db8:")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_generate_random_different_addresses(self):
        """Test that generated addresses are different."""
        addr1 = generate_random_ipv6()
        addr2 = generate_random_ipv6()
        # Very unlikely to be the same
        assert addr1 != addr2


class TestReversePointer:
    """Test reverse DNS pointer generation."""

    def test_reverse_pointer_simple(self):
        """Test reverse pointer for simple address."""
        ptr = reverse_pointer("::1")
        assert ptr.endswith(".ip6.arpa")
        assert ptr.startswith("1.0.0.0")

    def test_reverse_pointer_complex(self):
        """Test reverse pointer for complex address."""
        ptr = reverse_pointer("2001:db8::1")
        assert ptr.endswith(".ip6.arpa")

    def test_reverse_pointer_with_zone(self):
        """Test reverse pointer with zone ID."""
        ptr = reverse_pointer("fe80::1%eth0")
        assert ptr.endswith(".ip6.arpa")


class TestMACToIPv6:
    """Test MAC to IPv6 link-local conversion."""

    def test_mac_to_ipv6_colon_format(self):
        """Test MAC in colon format."""
        mac = "00:11:22:33:44:55"
        addr = mac_to_ipv6_link_local(mac)
        assert addr.startswith("fe80::")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_mac_to_ipv6_dash_format(self):
        """Test MAC in dash format."""
        mac = "00-11-22-33-44-55"
        addr = mac_to_ipv6_link_local(mac)
        assert addr.startswith("fe80::")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_mac_to_ipv6_no_separator(self):
        """Test MAC without separator."""
        mac = "001122334455"
        addr = mac_to_ipv6_link_local(mac)
        assert addr.startswith("fe80::")
        from ipv6tools.validator import is_valid_ipv6
        assert is_valid_ipv6(addr)

    def test_mac_to_ipv6_eui64(self):
        """Test EUI-64 conversion."""
        # Known MAC address conversion
        mac = "00:00:00:00:00:00"
        addr = mac_to_ipv6_link_local(mac)
        # Should have fffe inserted and bit flipped
        from ipv6tools.utils import expand_address
        expanded = expand_address(addr)
        assert "fffe" in expanded

    def test_mac_to_ipv6_invalid_length(self):
        """Test invalid MAC length."""
        with pytest.raises(ValueError):
            mac_to_ipv6_link_local("00:11:22")

    def test_mac_to_ipv6_invalid_format(self):
        """Test invalid MAC format."""
        with pytest.raises(ValueError):
            mac_to_ipv6_link_local("gg:hh:ii:jj:kk:ll")


class TestSubnetMask:
    """Test subnet mask calculation."""

    def test_calculate_subnet_mask_0(self):
        """Test /0 prefix."""
        mask = calculate_subnet_mask(0)
        assert mask == "::"

    def test_calculate_subnet_mask_64(self):
        """Test /64 prefix."""
        mask = calculate_subnet_mask(64)
        assert mask == "ffff:ffff:ffff:ffff::"

    def test_calculate_subnet_mask_128(self):
        """Test /128 prefix."""
        mask = calculate_subnet_mask(128)
        assert mask == "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"

    def test_calculate_subnet_mask_invalid(self):
        """Test invalid prefix length."""
        with pytest.raises(ValueError):
            calculate_subnet_mask(-1)

        with pytest.raises(ValueError):
            calculate_subnet_mask(129)
