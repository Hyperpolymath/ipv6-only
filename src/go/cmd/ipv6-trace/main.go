package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"time"
)

var (
	maxHops = flag.Int("m", 30, "maximum number of hops")
	timeout = flag.Duration("w", 5*time.Second, "timeout for each probe")
	queries = flag.Int("q", 3, "number of queries per hop")
	port    = flag.Int("p", 33434, "base port number")
	verbose = flag.Bool("v", "verbose output")
)

func main() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [options] <host>\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "\nIPv6 Traceroute Tool\n\n")
		fmt.Fprintf(os.Stderr, "Options:\n")
		flag.PrintDefaults()
	}

	flag.Parse()

	if flag.NArg() < 1 {
		flag.Usage()
		os.Exit(1)
	}

	target := flag.Arg(0)

	// Resolve target
	ips, err := net.LookupIP(target)
	if err != nil {
		log.Fatalf("Failed to resolve %s: %v", target, err)
	}

	// Find IPv6 address
	var targetIP net.IP
	for _, ip := range ips {
		if ip.To4() == nil && ip.To16() != nil {
			targetIP = ip
			break
		}
	}

	if targetIP == nil {
		log.Fatalf("No IPv6 address found for %s", target)
	}

	fmt.Printf("traceroute to %s (%s), %d hops max\n", target, targetIP, *maxHops)

	traceroute(targetIP)
}

func traceroute(target net.IP) {
	for ttl := 1; ttl <= *maxHops; ttl++ {
		fmt.Printf("%2d  ", ttl)

		responses := make([]string, *queries)
		durations := make([]time.Duration, *queries)

		for q := 0; q < *queries; q++ {
			start := time.Now()

			// Simulate traceroute probe
			// In production, use raw sockets and ICMPv6
			addr, duration, err := probe(target, ttl, *timeout)

			if err != nil {
				responses[q] = "*"
			} else {
				responses[q] = addr.String()
				durations[q] = duration
			}
		}

		// Print results for this hop
		printed := make(map[string]bool)
		for i, resp := range responses {
			if resp == "*" {
				if !printed["*"] {
					fmt.Print("*")
					printed["*"] = true
				}
			} else {
				if !printed[resp] {
					hostname := getHostname(resp)
					if hostname != "" {
						fmt.Printf(" %s (%s)", hostname, resp)
					} else {
						fmt.Printf(" %s", resp)
					}
					printed[resp] = true
				}
				fmt.Printf("  %.3f ms", float64(durations[i].Microseconds())/1000.0)
			}
		}
		fmt.Println()

		// Check if we reached destination
		for _, resp := range responses {
			if resp == target.String() {
				return
			}
		}
	}
}

func probe(target net.IP, ttl int, timeout time.Duration) (net.IP, time.Duration, error) {
	// Simplified probe - in production use raw sockets
	start := time.Now()

	// Simulate network delay
	time.Sleep(time.Duration(ttl*10) * time.Millisecond)

	duration := time.Since(start)

	// Simulate reaching target at some hop
	if ttl >= 5 {
		return target, duration, nil
	}

	// Simulate intermediate hop
	intermediateIP := net.ParseIP(fmt.Sprintf("2001:db8::%x", ttl))
	return intermediateIP, duration, nil
}

func getHostname(ipStr string) string {
	names, err := net.LookupAddr(ipStr)
	if err != nil || len(names) == 0 {
		return ""
	}
	return names[0]
}
