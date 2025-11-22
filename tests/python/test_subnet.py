"""
Tests for IPv6 subnet calculator module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/python'))

from ipv6tools.subnet import IPv6SubnetCalculator, SubnetInfo


class TestIPv6SubnetCalculator:
    """Test IPv6SubnetCalculator class."""

    def test_initialization(self):
        """Test creating calculator."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        assert calc.network.prefixlen == 32

    def test_initialization_invalid(self):
        """Test invalid network."""
        with pytest.raises(ValueError):
            IPv6SubnetCalculator("invalid")

    def test_get_info(self):
        """Test getting network info."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        info = calc.get_info()

        assert isinstance(info, SubnetInfo)
        assert info.network == "2001:db8::/32"
        assert info.prefix_length == 32
        assert info.network_address == "2001:db8::"

    def test_divide_into_subnets(self):
        """Test dividing network into subnets."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        subnets = calc.divide_into_subnets(4)

        assert len(subnets) == 4
        for subnet in subnets:
            assert isinstance(subnet, SubnetInfo)
            assert subnet.prefix_length == 34  # 32 + 2 bits for 4 subnets

    def test_divide_into_subnets_invalid_count(self):
        """Test invalid subnet count."""
        calc = IPv6SubnetCalculator("2001:db8::/32")

        with pytest.raises(ValueError):
            calc.divide_into_subnets(0)

        with pytest.raises(ValueError):
            calc.divide_into_subnets(-1)

    def test_divide_into_too_many_subnets(self):
        """Test dividing into too many subnets."""
        calc = IPv6SubnetCalculator("2001:db8::/127")

        with pytest.raises(ValueError):
            calc.divide_into_subnets(10)  # Would need /131

    def test_divide_by_prefix(self):
        """Test dividing by specific prefix."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        subnets = calc.divide_by_prefix(34)

        assert len(subnets) == 4  # 2^(34-32) = 4
        for subnet in subnets:
            assert subnet.prefix_length == 34

    def test_divide_by_prefix_invalid(self):
        """Test invalid prefix for division."""
        calc = IPv6SubnetCalculator("2001:db8::/32")

        with pytest.raises(ValueError):
            calc.divide_by_prefix(32)  # Same as current

        with pytest.raises(ValueError):
            calc.divide_by_prefix(31)  # Smaller than current

        with pytest.raises(ValueError):
            calc.divide_by_prefix(129)  # Too large

    def test_get_supernet(self):
        """Test getting supernet."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        supernet = calc.get_supernet(24)

        assert isinstance(supernet, SubnetInfo)
        assert supernet.prefix_length == 24
        assert supernet.network == "2001:d00::/24"

    def test_get_supernet_invalid(self):
        """Test invalid supernet prefix."""
        calc = IPv6SubnetCalculator("2001:db8::/32")

        with pytest.raises(ValueError):
            calc.get_supernet(32)  # Same as current

        with pytest.raises(ValueError):
            calc.get_supernet(33)  # Larger than current

        with pytest.raises(ValueError):
            calc.get_supernet(-1)  # Negative

    def test_contains_address(self):
        """Test checking if address is in network."""
        calc = IPv6SubnetCalculator("2001:db8::/32")

        assert calc.contains_address("2001:db8::1")
        assert calc.contains_address("2001:db8:ffff:ffff:ffff:ffff:ffff:ffff")
        assert not calc.contains_address("2001:db9::1")

    def test_contains_address_with_zone(self):
        """Test address with zone ID."""
        calc = IPv6SubnetCalculator("fe80::/10")
        assert calc.contains_address("fe80::1%eth0")

    def test_contains_address_invalid(self):
        """Test invalid address."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        assert not calc.contains_address("invalid")

    def test_overlaps_with(self):
        """Test network overlap detection."""
        calc = IPv6SubnetCalculator("2001:db8::/32")

        assert calc.overlaps_with("2001:db8:1::/48")  # Subset
        assert calc.overlaps_with("2001:db8::/32")  # Same
        assert not calc.overlaps_with("2001:db9::/32")  # Different

    def test_overlaps_with_invalid(self):
        """Test invalid network for overlap."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        assert not calc.overlaps_with("invalid")

    def test_get_summary_address_single(self):
        """Test summarizing networks."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        summary = calc.get_summary_address(["2001:db8:1::/48"])

        assert summary is not None
        assert "/32" in summary  # Should summarize to the /32

    def test_get_summary_address_multiple(self):
        """Test summarizing multiple networks."""
        calc = IPv6SubnetCalculator("2001:db8::/48")
        summary = calc.get_summary_address([
            "2001:db8:1::/48",
            "2001:db8:2::/48",
            "2001:db8:3::/48",
        ])

        assert summary is not None

    def test_get_summary_address_invalid(self):
        """Test invalid network in summary."""
        calc = IPv6SubnetCalculator("2001:db8::/32")

        with pytest.raises(ValueError):
            calc.get_summary_address(["invalid"])

    def test_recommend_allocation(self):
        """Test recommending subnet allocation."""
        departments = {
            "Engineering": 4,
            "Sales": 2,
            "HR": 1,
        }

        allocation = IPv6SubnetCalculator.recommend_allocation(
            "2001:db8::/32",
            departments
        )

        assert len(allocation) == 3
        assert "Engineering" in allocation
        assert len(allocation["Engineering"]) == 4
        assert len(allocation["Sales"]) == 2
        assert len(allocation["HR"]) == 1

        # Check that all subnets are SubnetInfo
        for dept_subnets in allocation.values():
            for subnet in dept_subnets:
                assert isinstance(subnet, SubnetInfo)

    def test_recommend_allocation_too_many(self):
        """Test allocation with too many subnets."""
        departments = {
            "Dept1": 1000000,  # Way too many
        }

        with pytest.raises(ValueError):
            IPv6SubnetCalculator.recommend_allocation(
                "2001:db8::/127",
                departments
            )


class TestSubnetInfo:
    """Test SubnetInfo dataclass."""

    def test_subnet_info_creation(self):
        """Test creating SubnetInfo."""
        info = SubnetInfo(
            network="2001:db8::/32",
            network_address="2001:db8::",
            first_address="2001:db8::",
            last_address="2001:db8:ffff:ffff:ffff:ffff:ffff:ffff",
            prefix_length=32,
            num_addresses=2**96,
            netmask="ffff:ffff::"
        )

        assert info.network == "2001:db8::/32"
        assert info.prefix_length == 32
        assert info.network_address == "2001:db8::"
