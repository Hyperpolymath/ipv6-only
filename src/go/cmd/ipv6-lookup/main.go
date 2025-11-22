package main

import (
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
	"time"
)

var (
	queryType  = flag.String("t", "AAAA", "query type (AAAA, PTR, ANY)")
	server     = flag.String("s", "", "DNS server to query (default: system resolver)")
	port       = flag.Int("p", 53, "DNS server port")
	timeout    = flag.Duration("w", 5*time.Second, "query timeout")
	verbose    = flag.Bool("v", false, "verbose output")
	short      = flag.Bool("short", false, "short output (addresses only)")
	reverse    = flag.Bool("x", false, "reverse lookup (PTR)")
	trace      = flag.Bool("trace", false, "trace delegation path")
)

func main() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [options] <hostname|address>\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "\nIPv6 DNS Lookup Tool\n\n")
		fmt.Fprintf(os.Stderr, "Options:\n")
		flag.PrintDefaults()
		fmt.Fprintf(os.Stderr, "\nExamples:\n")
		fmt.Fprintf(os.Stderr, "  %s google.com\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  %s -x 2001:4860:4860::8888\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  %s -s 2001:4860:4860::8888 cloudflare.com\n", os.Args[0])
	}

	flag.Parse()

	if flag.NArg() < 1 {
		flag.Usage()
		os.Exit(1)
	}

	target := flag.Arg(0)

	if *reverse {
		lookupPTR(target)
	} else {
		lookupAAAA(target)
	}
}

func lookupAAAA(hostname string) {
	if *verbose {
		fmt.Printf("Looking up AAAA records for %s...\n", hostname)
		if *server != "" {
			fmt.Printf("Using DNS server: %s:%d\n", *server, *port)
		}
		fmt.Println()
	}

	// Lookup IPv6 addresses
	ips, err := net.LookupIP(hostname)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	// Filter IPv6 addresses
	var ipv6Addrs []net.IP
	for _, ip := range ips {
		if ip.To4() == nil && ip.To16() != nil {
			ipv6Addrs = append(ipv6Addrs, ip)
		}
	}

	if len(ipv6Addrs) == 0 {
		fmt.Printf("No IPv6 (AAAA) records found for %s\n", hostname)

		// Also check for IPv4
		var ipv4Count int
		for _, ip := range ips {
			if ip.To4() != nil {
				ipv4Count++
			}
		}
		if ipv4Count > 0 {
			fmt.Printf("(Found %d IPv4 address(es), but no IPv6)\n", ipv4Count)
		}
		return
	}

	if *short {
		// Short output - addresses only
		for _, ip := range ipv6Addrs {
			fmt.Println(ip)
		}
	} else {
		// Full output
		fmt.Printf("%s has IPv6 address", hostname)
		if len(ipv6Addrs) > 1 {
			fmt.Printf("es")
		}
		fmt.Println()

		for i, ip := range ipv6Addrs {
			fmt.Printf("  [%d] %s\n", i+1, ip)

			if *verbose {
				// Try reverse lookup
				names, err := net.LookupAddr(ip.String())
				if err == nil && len(names) > 0 {
					fmt.Printf("      PTR: %s\n", strings.Join(names, ", "))
				}
			}
		}
	}
}

func lookupPTR(address string) {
	if *verbose {
		fmt.Printf("Looking up PTR record for %s...\n", address)
		fmt.Println()
	}

	// Validate IPv6 address
	ip := net.ParseIP(address)
	if ip == nil {
		fmt.Fprintf(os.Stderr, "Error: Invalid IPv6 address: %s\n", address)
		os.Exit(1)
	}

	if ip.To4() != nil {
		fmt.Fprintf(os.Stderr, "Error: %s is an IPv4 address, not IPv6\n", address)
		os.Exit(1)
	}

	// Perform reverse lookup
	names, err := net.LookupAddr(address)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	if len(names) == 0 {
		fmt.Printf("No PTR record found for %s\n", address)
		return
	}

	if *short {
		// Short output
		for _, name := range names {
			fmt.Println(strings.TrimSuffix(name, "."))
		}
	} else {
		// Full output
		fmt.Printf("%s has PTR record", address)
		if len(names) > 1 {
			fmt.Printf("s")
		}
		fmt.Println()

		for i, name := range names {
			fmt.Printf("  [%d] %s\n", i+1, strings.TrimSuffix(name, "."))
		}
	}
}
