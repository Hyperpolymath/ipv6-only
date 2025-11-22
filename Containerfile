# Containerfile for IPv6-Only Tools
# Using Chainguard Wolfi for supply chain security
# Build with: podman build -f Containerfile -t ipv6-only .

# Stage 1: Build environment
FROM cgr.dev/chainguard/wolfi-base:latest AS builder

# Install build dependencies
RUN apk add --no-cache \
    python-3.12 \
    py3-pip \
    go \
    git \
    gcc \
    musl-dev \
    linux-headers

WORKDIR /build

# Copy source
COPY src/ ./src/
COPY setup.py requirements.txt ./
COPY pyproject.toml ./

# Build Python package
RUN pip install --no-cache-dir build && \
    python -m build

# Build Go tools
WORKDIR /build/src/go
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-s -w" -o /bin/ipv6-ping ./cmd/ipv6-ping
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-s -w" -o /bin/ipv6-scan ./cmd/ipv6-scan
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-s -w" -o /bin/ipv6-trace ./cmd/ipv6-trace
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-s -w" -o /bin/ipv6-lookup ./cmd/ipv6-lookup

# Stage 2: Runtime environment
FROM cgr.dev/chainguard/wolfi-base:latest

LABEL maintainer="IPv6-Only Tools Project"
LABEL description="Comprehensive IPv6 networking tools and utilities"
LABEL org.opencontainers.image.source="https://github.com/Hyperpolymath/ipv6-only"
LABEL org.opencontainers.image.description="IPv6-only networking tools with Chainguard Wolfi base for supply chain security"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.version="0.1.0"

# Install runtime dependencies
RUN apk add --no-cache \
    python-3.12 \
    py3-pip \
    iproute2 \
    iputils \
    bind-tools \
    tcpdump \
    curl \
    jq \
    bash

# Create non-root user
RUN addgroup -g 1000 ipv6tools && \
    adduser -D -u 1000 -G ipv6tools ipv6tools

WORKDIR /app

# Copy built artifacts from builder
COPY --from=builder /build/dist/*.whl /tmp/
COPY --from=builder /bin/ipv6-* /usr/local/bin/

# Install Python package
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl

# Copy scripts and make executable
COPY src/scripts/*.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

# Copy web interface
COPY src/web/ /app/web/

# Copy configuration
COPY config/ /app/config/

# Copy documentation
COPY docs/*.adoc /app/docs/

# Create directories for data and output
RUN mkdir -p /data /output /config && \
    chown -R ipv6tools:ipv6tools /app /data /output /config

# Set up IPv6
RUN echo "net.ipv6.conf.all.disable_ipv6 = 0" >> /etc/sysctl.conf && \
    echo "net.ipv6.conf.default.disable_ipv6 = 0" >> /etc/sysctl.conf && \
    echo "net.ipv6.conf.all.forwarding = 0" >> /etc/sysctl.conf

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:${PATH}" \
    IPV6_TOOLS_CONFIG="/app/config/ipv6-tools.ncl" \
    IPV6_TOOLS_DATA="/data"

# Switch to non-root user
USER ipv6tools

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import ipv6tools; import sys; sys.exit(0)" || exit 1

# Expose ports for web interface
EXPOSE 8000 8443

# Default command
CMD ["/bin/bash"]

# Volume mounts
VOLUME ["/data", "/output", "/config"]

# Security labels
LABEL org.opencontainers.image.vendor="IPv6-Only Project"
LABEL org.opencontainers.image.title="IPv6-Only Tools"
LABEL org.opencontainers.image.documentation="https://github.com/Hyperpolymath/ipv6-only/blob/main/README.adoc"
LABEL com.chainguard.wolfi="true"
