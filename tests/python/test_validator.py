"""
Tests for IPv6 validator module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/python'))

from ipv6tools.validator import (
    is_valid_ipv6,
    validate_ipv6,
    is_valid_ipv6_network,
    validate_ipv6_network,
    is_compressed_format,
    is_expanded_format,
    validate_prefix_length,
    is_valid_prefix_length,
)


class TestIsValidIPv6:
    """Test is_valid_ipv6 function."""

    def test_valid_addresses(self):
        """Test valid IPv6 addresses."""
        valid = [
            "2001:db8::1",
            "::1",
            "::",
            "fe80::1",
            "2001:0db8:0000:0000:0000:0000:0000:0001",
            "ff02::1",
        ]
        for addr in valid:
            assert is_valid_ipv6(addr), f"{addr} should be valid"

    def test_invalid_addresses(self):
        """Test invalid IPv6 addresses."""
        invalid = [
            "",
            "invalid",
            "192.168.1.1",  # IPv4
            "2001:db8:::1",  # Too many colons
            "gggg::1",  # Invalid hex
            "2001:db8:0:0:0:0:0:0:1",  # Too many groups
        ]
        for addr in invalid:
            assert not is_valid_ipv6(addr), f"{addr} should be invalid"

    def test_zone_id_allowed(self):
        """Test zone ID handling."""
        assert is_valid_ipv6("fe80::1%eth0", allow_zone=True)
        assert not is_valid_ipv6("fe80::1%eth0", allow_zone=False)

    def test_zone_id_invalid(self):
        """Test invalid zone ID."""
        assert not is_valid_ipv6("fe80::1%", allow_zone=True)  # Empty zone


class TestValidateIPv6:
    """Test validate_ipv6 function."""

    def test_valid_returns_true_none(self):
        """Test valid address returns (True, None)."""
        valid, error = validate_ipv6("2001:db8::1")
        assert valid is True
        assert error is None

    def test_invalid_returns_false_message(self):
        """Test invalid address returns (False, message)."""
        valid, error = validate_ipv6("invalid")
        assert valid is False
        assert error is not None
        assert isinstance(error, str)

    def test_empty_address(self):
        """Test empty address."""
        valid, error = validate_ipv6("")
        assert valid is False
        assert "empty" in error.lower()

    def test_zone_id_validation(self):
        """Test zone ID validation."""
        valid, error = validate_ipv6("fe80::1%eth0", allow_zone=True)
        assert valid is True
        assert error is None

        valid, error = validate_ipv6("fe80::1%eth0", allow_zone=False)
        assert valid is False

    def test_empty_zone_id(self):
        """Test empty zone ID."""
        valid, error = validate_ipv6("fe80::1%", allow_zone=True)
        assert valid is False
        assert "zone" in error.lower()


class TestIsValidIPv6Network:
    """Test is_valid_ipv6_network function."""

    def test_valid_networks(self):
        """Test valid networks."""
        valid = [
            "2001:db8::/32",
            "fe80::/10",
            "::/0",
            "2001:db8:1234::/48",
        ]
        for net in valid:
            assert is_valid_ipv6_network(net), f"{net} should be valid"

    def test_invalid_networks(self):
        """Test invalid networks."""
        invalid = [
            "",
            "2001:db8::",  # Missing prefix
            "invalid/32",
            "2001:db8::/129",  # Prefix too large
            "192.168.0.0/24",  # IPv4
        ]
        for net in invalid:
            assert not is_valid_ipv6_network(net), f"{net} should be invalid"


class TestValidateIPv6Network:
    """Test validate_ipv6_network function."""

    def test_valid_network(self):
        """Test valid network."""
        valid, error = validate_ipv6_network("2001:db8::/32")
        assert valid is True
        assert error is None

    def test_missing_prefix(self):
        """Test network without prefix."""
        valid, error = validate_ipv6_network("2001:db8::")
        assert valid is False
        assert "prefix" in error.lower()

    def test_invalid_prefix(self):
        """Test invalid prefix length."""
        valid, error = validate_ipv6_network("2001:db8::/129")
        assert valid is False


class TestFormatChecking:
    """Test format checking functions."""

    def test_is_compressed_format(self):
        """Test compressed format detection."""
        assert is_compressed_format("2001:db8::1")
        assert is_compressed_format("::1")
        assert is_compressed_format("::")
        assert not is_compressed_format("2001:0db8:0000:0000:0000:0000:0000:0001")

    def test_is_expanded_format(self):
        """Test expanded format detection."""
        assert is_expanded_format("2001:0db8:0000:0000:0000:0000:0000:0001")
        assert not is_expanded_format("2001:db8::1")
        assert not is_expanded_format("::1")


class TestPrefixLengthValidation:
    """Test prefix length validation."""

    def test_valid_prefix_lengths(self):
        """Test valid prefix lengths."""
        for i in range(0, 129):
            assert is_valid_prefix_length(i)
            valid, error = validate_prefix_length(i)
            assert valid is True
            assert error is None

    def test_invalid_prefix_lengths(self):
        """Test invalid prefix lengths."""
        invalid = [-1, 129, 200]
        for prefix in invalid:
            assert not is_valid_prefix_length(prefix)
            valid, error = validate_prefix_length(prefix)
            assert valid is False
            assert error is not None

    def test_non_integer_prefix(self):
        """Test non-integer prefix."""
        assert not is_valid_prefix_length("32")
        assert not is_valid_prefix_length(32.5)
        valid, error = validate_prefix_length("32")
        assert valid is False
        assert "integer" in error.lower()
