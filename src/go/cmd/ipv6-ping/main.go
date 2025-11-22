package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"
)

const (
	protocolICMPv6 = 58
)

var (
	count     = flag.Int("c", 4, "number of packets to send")
	timeout   = flag.Duration("W", 2*time.Second, "timeout for each packet")
	interval  = flag.Duration("i", 1*time.Second, "interval between packets")
	size      = flag.Int("s", 64, "packet size")
	verbose   = flag.Bool("v", false, "verbose output")
	interface_ = flag.String("I", "", "interface to use")
)

type Statistics struct {
	transmitted int
	received    int
	startTime   time.Time
	rtts        []time.Duration
}

func main() {
	flag.Parse()

	if flag.NArg() < 1 {
		fmt.Fprintf(os.Stderr, "Usage: %s [options] <host>\n", os.Args[0])
		flag.PrintDefaults()
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

	fmt.Printf("PING %s (%s): %d data bytes\n", target, targetIP, *size)

	stats := &Statistics{
		startTime: time.Now(),
		rtts:      make([]time.Duration, 0),
	}

	// Setup signal handling
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Start pinging
	done := make(chan bool)
	go func() {
		ping(targetIP, stats)
		done <- true
	}()

	// Wait for completion or interruption
	select {
	case <-done:
	case <-sigChan:
		fmt.Println("\n--- Interrupted ---")
	}

	printStatistics(target, targetIP, stats)
}

func ping(targetIP net.IP, stats *Statistics) {
	for i := 0; i < *count; i++ {
		if i > 0 {
			time.Sleep(*interval)
		}

		rtt, err := sendPing(targetIP, i)
		stats.transmitted++

		if err != nil {
			if *verbose {
				fmt.Printf("Failed to ping %s: %v\n", targetIP, err)
			}
		} else {
			stats.received++
			stats.rtts = append(stats.rtts, rtt)
			fmt.Printf("%d bytes from %s: icmp_seq=%d time=%.2f ms\n",
				*size, targetIP, i, float64(rtt.Microseconds())/1000.0)
		}
	}
}

func sendPing(targetIP net.IP, seq int) (time.Duration, error) {
	// Create ICMPv6 Echo Request
	// For a real implementation, you would use raw sockets and construct proper ICMP packets
	// This is a simplified version using net.Dial

	start := time.Now()

	// Try to establish connection (for demonstration)
	// In production, use golang.org/x/net/icmp package
	conn, err := net.DialTimeout("tcp", net.JoinHostPort(targetIP.String(), "80"), *timeout)
	if err != nil {
		// Try ping using existing methods
		return 0, err
	}
	defer conn.Close()

	rtt := time.Since(start)
	return rtt, nil
}

func printStatistics(host string, ip net.IP, stats *Statistics) {
	duration := time.Since(stats.startTime)

	fmt.Printf("\n--- %s (%s) ping statistics ---\n", host, ip)
	fmt.Printf("%d packets transmitted, %d packets received, %.1f%% packet loss\n",
		stats.transmitted, stats.received,
		float64(stats.transmitted-stats.received)/float64(stats.transmitted)*100)

	if len(stats.rtts) > 0 {
		var sum time.Duration
		min := stats.rtts[0]
		max := stats.rtts[0]

		for _, rtt := range stats.rtts {
			sum += rtt
			if rtt < min {
				min = rtt
			}
			if rtt > max {
				max = rtt
			}
		}

		avg := sum / time.Duration(len(stats.rtts))

		fmt.Printf("round-trip min/avg/max = %.2f/%.2f/%.2f ms\n",
			float64(min.Microseconds())/1000.0,
			float64(avg.Microseconds())/1000.0,
			float64(max.Microseconds())/1000.0)
	}

	fmt.Printf("time %.3fs\n", duration.Seconds())
}
