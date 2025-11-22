"""
Performance benchmarking suite for IPv6 operations.
"""

import time
import statistics
from typing import List, Dict, Callable
from dataclasses import dataclass
import random

from .address import IPv6Address, IPv6Network
from .subnet import IPv6SubnetCalculator
from .utils import (
    compress_address, expand_address, generate_link_local,
    generate_unique_local, mac_to_ipv6_link_local
)
from .validator import is_valid_ipv6, validate_ipv6


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    ops_per_second: float
    std_dev: float


class IPv6Benchmark:
    """Benchmark suite for IPv6 operations."""

    def __init__(self, iterations: int = 10000):
        """
        Initialize benchmark.

        Args:
            iterations: Number of iterations for each test
        """
        self.iterations = iterations
        self.results: List[BenchmarkResult] = []

    def run_benchmark(self, name: str, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """
        Run a benchmark test.

        Args:
            name: Test name
            func: Function to benchmark
            *args: Arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            BenchmarkResult
        """
        times = []

        # Warmup
        for _ in range(min(100, self.iterations // 10)):
            func(*args, **kwargs)

        # Actual benchmark
        for _ in range(self.iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)

        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        ops_per_second = self.iterations / total_time

        result = BenchmarkResult(
            name=name,
            iterations=self.iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            ops_per_second=ops_per_second,
            std_dev=std_dev
        )

        self.results.append(result)
        return result

    def benchmark_address_creation(self) -> BenchmarkResult:
        """Benchmark IPv6Address creation."""
        test_addr = "2001:db8::1"
        return self.run_benchmark(
            "IPv6Address creation",
            lambda: IPv6Address(test_addr)
        )

    def benchmark_address_validation(self) -> BenchmarkResult:
        """Benchmark address validation."""
        test_addr = "2001:db8::1"
        return self.run_benchmark(
            "Address validation",
            lambda: is_valid_ipv6(test_addr)
        )

    def benchmark_address_validation_detailed(self) -> BenchmarkResult:
        """Benchmark detailed address validation."""
        test_addr = "2001:db8::1"
        return self.run_benchmark(
            "Detailed validation",
            lambda: validate_ipv6(test_addr)
        )

    def benchmark_compression(self) -> BenchmarkResult:
        """Benchmark address compression."""
        test_addr = "2001:0db8:0000:0000:0000:0000:0000:0001"
        return self.run_benchmark(
            "Address compression",
            lambda: compress_address(test_addr)
        )

    def benchmark_expansion(self) -> BenchmarkResult:
        """Benchmark address expansion."""
        test_addr = "2001:db8::1"
        return self.run_benchmark(
            "Address expansion",
            lambda: expand_address(test_addr)
        )

    def benchmark_network_creation(self) -> BenchmarkResult:
        """Benchmark IPv6Network creation."""
        test_net = "2001:db8::/32"
        return self.run_benchmark(
            "IPv6Network creation",
            lambda: IPv6Network(test_net)
        )

    def benchmark_network_contains(self) -> BenchmarkResult:
        """Benchmark network membership test."""
        net = IPv6Network("2001:db8::/32")
        test_addr = "2001:db8::1"
        return self.run_benchmark(
            "Network contains check",
            lambda: net.contains(test_addr)
        )

    def benchmark_subnet_calculation(self) -> BenchmarkResult:
        """Benchmark subnet calculation."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        return self.run_benchmark(
            "Subnet calculation",
            lambda: calc.get_info()
        )

    def benchmark_subnet_division(self) -> BenchmarkResult:
        """Benchmark subnet division."""
        calc = IPv6SubnetCalculator("2001:db8::/32")
        return self.run_benchmark(
            "Subnet division (4 subnets)",
            lambda: calc.divide_into_subnets(4)
        )

    def benchmark_link_local_generation(self) -> BenchmarkResult:
        """Benchmark link-local address generation."""
        return self.run_benchmark(
            "Link-local generation",
            generate_link_local
        )

    def benchmark_ula_generation(self) -> BenchmarkResult:
        """Benchmark ULA generation."""
        return self.run_benchmark(
            "ULA generation",
            generate_unique_local
        )

    def benchmark_mac_conversion(self) -> BenchmarkResult:
        """Benchmark MAC to IPv6 conversion."""
        test_mac = "00:11:22:33:44:55"
        return self.run_benchmark(
            "MAC to IPv6 conversion",
            lambda: mac_to_ipv6_link_local(test_mac)
        )

    def run_all(self) -> List[BenchmarkResult]:
        """
        Run all benchmarks.

        Returns:
            List of all results
        """
        print(f"Running benchmarks with {self.iterations} iterations each...\n")

        tests = [
            self.benchmark_address_creation,
            self.benchmark_address_validation,
            self.benchmark_address_validation_detailed,
            self.benchmark_compression,
            self.benchmark_expansion,
            self.benchmark_network_creation,
            self.benchmark_network_contains,
            self.benchmark_subnet_calculation,
            self.benchmark_subnet_division,
            self.benchmark_link_local_generation,
            self.benchmark_ula_generation,
            self.benchmark_mac_conversion,
        ]

        for test in tests:
            result = test()
            self.print_result(result)

        return self.results

    def print_result(self, result: BenchmarkResult):
        """Print benchmark result."""
        print(f"{result.name:40s} | {result.ops_per_second:12,.0f} ops/s | "
              f"{result.avg_time*1000000:8.2f} µs avg | "
              f"{result.min_time*1000000:8.2f} µs min | "
              f"{result.max_time*1000000:8.2f} µs max")

    def print_summary(self):
        """Print summary of all results."""
        if not self.results:
            print("No benchmark results available")
            return

        print("\n" + "="*100)
        print("BENCHMARK SUMMARY")
        print("="*100)
        print(f"{'Test':<40s} | {'Ops/Second':>12s} | {'Avg Time':>10s} | {'Min Time':>10s} | {'Max Time':>10s}")
        print("-"*100)

        for result in sorted(self.results, key=lambda r: r.ops_per_second, reverse=True):
            self.print_result(result)

        print("="*100)
        print(f"\nFastest: {self.results[0].name} ({self.results[0].ops_per_second:,.0f} ops/s)")

        slowest = min(self.results, key=lambda r: r.ops_per_second)
        print(f"Slowest: {slowest.name} ({slowest.ops_per_second:,.0f} ops/s)")

        avg_ops = statistics.mean(r.ops_per_second for r in self.results)
        print(f"Average: {avg_ops:,.0f} ops/s")

    def compare_implementations(self):
        """Compare different implementation approaches."""
        print("\n" + "="*100)
        print("IMPLEMENTATION COMPARISON")
        print("="*100)

        # Compare different validation approaches
        test_addr = "2001:db8::1"

        # Approach 1: Simple check
        result1 = self.run_benchmark(
            "Simple validation",
            lambda: is_valid_ipv6(test_addr)
        )

        # Approach 2: Detailed validation
        result2 = self.run_benchmark(
            "Detailed validation",
            lambda: validate_ipv6(test_addr)
        )

        print(f"\nValidation comparison:")
        print(f"  Simple:   {result1.ops_per_second:,.0f} ops/s")
        print(f"  Detailed: {result2.ops_per_second:,.0f} ops/s")
        print(f"  Speedup:  {result1.ops_per_second / result2.ops_per_second:.2f}x")

        # Compare address formats
        compressed = "2001:db8::1"
        expanded = "2001:0db8:0000:0000:0000:0000:0000:0001"

        result3 = self.run_benchmark(
            "Parse compressed",
            lambda: IPv6Address(compressed)
        )

        result4 = self.run_benchmark(
            "Parse expanded",
            lambda: IPv6Address(expanded)
        )

        print(f"\nParsing comparison:")
        print(f"  Compressed: {result3.ops_per_second:,.0f} ops/s")
        print(f"  Expanded:   {result4.ops_per_second:,.0f} ops/s")
        print(f"  Speedup:    {result3.ops_per_second / result4.ops_per_second:.2f}x")


def benchmark_cli():
    """Command-line interface for benchmarks."""
    import argparse

    parser = argparse.ArgumentParser(description="IPv6 Performance Benchmarks")
    parser.add_argument("-n", "--iterations", type=int, default=10000,
                       help="Number of iterations per test")
    parser.add_argument("-q", "--quick", action="store_true",
                       help="Quick mode (fewer iterations)")
    parser.add_argument("-c", "--compare", action="store_true",
                       help="Run implementation comparisons")

    args = parser.parse_args()

    iterations = 1000 if args.quick else args.iterations

    bench = IPv6Benchmark(iterations=iterations)

    print("="*100)
    print(f"IPv6 PERFORMANCE BENCHMARKS")
    print(f"Iterations per test: {iterations:,}")
    print("="*100)
    print()

    bench.run_all()
    bench.print_summary()

    if args.compare:
        bench.compare_implementations()

    print("\nBenchmark complete!")


if __name__ == "__main__":
    benchmark_cli()
