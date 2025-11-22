package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"sync"
	"time"
)

var (
	network   = flag.String("n", "", "IPv6 network to scan (CIDR notation)")
	ports     = flag.String("p", "80,443,22,21,25,53", "Comma-separated list of ports to scan")
	timeout   = flag.Duration("t", 500*time.Millisecond, "connection timeout")
	workers   = flag.Int("w", 100, "number of concurrent workers")
	verbose   = flag.Bool("v", false, "verbose output")
	linklocal = flag.Bool("l", false, "scan link-local addresses")
)

type ScanResult struct {
	IP   string
	Port int
	Open bool
}

func main() {
	flag.Parse()

	if *network == "" && flag.NArg() == 0 {
		fmt.Fprintf(os.Stderr, "Usage: %s -n <network> or %s <address>\n", os.Args[0], os.Args[0])
		flag.PrintDefaults()
		os.Exit(1)
	}

	var addresses []string

	if *network != "" {
		// Scan network
		addrs, err := generateAddresses(*network)
		if err != nil {
			log.Fatalf("Failed to generate addresses: %v", err)
		}
		addresses = addrs
	} else {
		// Scan single address
		addresses = []string{flag.Arg(0)}
	}

	// Parse ports
	portList := parsePorts(*ports)

	fmt.Printf("Starting IPv6 scan of %d address(es) on %d port(s)\n", len(addresses), len(portList))
	fmt.Printf("Timeout: %v, Workers: %d\n\n", *timeout, *workers)

	results := make(chan ScanResult, *workers)
	var wg sync.WaitGroup

	// Worker pool
	jobs := make(chan struct {
		addr string
		port int
	}, *workers)

	for i := 0; i < *workers; i++ {
		go worker(jobs, results, &wg)
	}

	// Send jobs
	go func() {
		for _, addr := range addresses {
			for _, port := range portList {
				wg.Add(1)
				jobs <- struct {
					addr string
					port int
				}{addr, port}
			}
		}
		close(jobs)
	}()

	// Collect results
	go func() {
		wg.Wait()
		close(results)
	}()

	// Print results
	openPorts := 0
	for result := range results {
		if result.Open {
			fmt.Printf("[+] %s:%d OPEN\n", result.IP, result.Port)
			openPorts++
		} else if *verbose {
			fmt.Printf("[-] %s:%d closed\n", result.IP, result.Port)
		}
	}

	fmt.Printf("\nScan complete. Found %d open port(s)\n", openPorts)
}

func worker(jobs <-chan struct {
	addr string
	port int
}, results chan<- ScanResult, wg *sync.WaitGroup) {
	for job := range jobs {
		open := scanPort(job.addr, job.port)
		results <- ScanResult{
			IP:   job.addr,
			Port: job.port,
			Open: open,
		}
		wg.Done()
	}
}

func scanPort(address string, port int) bool {
	target := net.JoinHostPort(address, fmt.Sprintf("%d", port))
	conn, err := net.DialTimeout("tcp6", target, *timeout)

	if err != nil {
		return false
	}

	conn.Close()
	return true
}

func generateAddresses(cidr string) ([]string, error) {
	ip, ipnet, err := net.ParseCIDR(cidr)
	if err != nil {
		return nil, err
	}

	// For IPv6, we can't enumerate all addresses in large networks
	// So we'll scan common patterns
	prefix, _ := ipnet.Mask.Size()

	if prefix < 120 {
		// Network too large, scan common addresses
		return generateCommonAddresses(ipnet), nil
	}

	// For /120 and larger, we can enumerate
	var addresses []string
	for ip := ip.Mask(ipnet.Mask); ipnet.Contains(ip); inc(ip) {
		addresses = append(addresses, ip.String())

		// Safety limit
		if len(addresses) >= 256 {
			break
		}
	}

	return addresses, nil
}

func generateCommonAddresses(ipnet *net.IPNet) []string {
	// Generate common host addresses within the network
	baseIP := ipnet.IP

	addresses := []string{
		baseIP.String(), // Network address
	}

	// Add common host IDs
	commonHosts := []uint64{
		1, 2, 10, 100, 254, 255,
		0x1, 0x2, 0x10, 0xfe, 0xff,
	}

	for _, hostID := range commonHosts {
		ip := make(net.IP, len(baseIP))
		copy(ip, baseIP)

		// Set last 64 bits to hostID
		for i := 0; i < 8 && hostID > 0; i++ {
			ip[15-i] = byte(hostID & 0xff)
			hostID >>= 8
		}

		if ipnet.Contains(ip) {
			addresses = append(addresses, ip.String())
		}
	}

	return addresses
}

func inc(ip net.IP) {
	for j := len(ip) - 1; j >= 0; j-- {
		ip[j]++
		if ip[j] > 0 {
			break
		}
	}
}

func parsePorts(portStr string) []int {
	var ports []int
	// Simple implementation - just parse comma-separated numbers
	var port int
	for i := 0; i < len(portStr); i++ {
		if portStr[i] >= '0' && portStr[i] <= '9' {
			port = port*10 + int(portStr[i]-'0')
		} else if portStr[i] == ',' || i == len(portStr)-1 {
			if port > 0 {
				ports = append(ports, port)
			}
			port = 0
		}
	}
	if port > 0 {
		ports = append(ports, port)
	}
	return ports
}
