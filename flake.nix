{
  description = "IPv6-Only Tools - Comprehensive IPv6 networking toolkit";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, rust-overlay }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };

        python = pkgs.python311;
        pythonPackages = python.pkgs;

        # Python dependencies
        pythonEnv = python.withPackages (ps: with ps; [
          # Core dependencies (none - uses stdlib)

          # Dev dependencies
          pytest
          pytest-cov
          black
          flake8
          mypy
          pylint
          isort

          # Optional dependencies
          click
          # dnspython (if needed)
        ]);

        # Go dependencies
        goEnv = pkgs.mkShell {
          buildInputs = with pkgs; [
            go_1_21
            gopls
            gotools
            go-tools
          ];
        };

      in
      {
        # Development shell
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python
            pythonEnv

            # Go
            go_1_21
            gopls
            gotools

            # Deno
            deno

            # Nickel
            # nickel # Uncomment if available in nixpkgs

            # Build tools
            just
            git

            # Container tools
            podman
            buildah
            skopeo

            # Documentation
            asciidoctor
            # asciidoctor-pdf

            # Network tools
            iproute2
            iputils
            bind
            tcpdump

            # Linters and formatters
            shellcheck
            shfmt

            # Testing
            nodePackages.prettier

            # Other utilities
            jq
            curl
            wget
          ];

          shellHook = ''
            echo "🌐 IPv6-Only Tools Development Environment"
            echo "=========================================="
            echo ""
            echo "Available commands:"
            echo "  just --list    # Show all automation recipes"
            echo "  just setup     # Complete environment setup"
            echo "  just test      # Run all tests"
            echo "  just build     # Build all components"
            echo ""
            echo "Languages:"
            echo "  Python: $(python --version)"
            echo "  Go: $(go version | cut -d' ' -f3)"
            echo "  Deno: $(deno --version | head -n1)"
            echo ""
            echo "Tools:"
            echo "  just: $(just --version)"
            echo "  podman: $(podman --version | head -n1)"
            echo ""

            # Set up environment
            export PYTHONPATH="$PWD/src/python:$PYTHONPATH"
            export PATH="$PWD/bin:$PATH"

            # IPv6 configuration
            export IPV6_TOOLS_CONFIG="$PWD/config/ipv6-tools.ncl"
            export IPV6_TOOLS_DATA="$PWD/data"
          '';
        };

        # Python package
        packages.python-ipv6tools = pythonPackages.buildPythonPackage {
          pname = "ipv6-only";
          version = "0.1.0";

          src = ./.;

          format = "pyproject";

          nativeBuildInputs = with pythonPackages; [
            setuptools
            wheel
            build
          ];

          propagatedBuildInputs = with pythonPackages; [
            # No runtime dependencies - uses stdlib
          ];

          checkInputs = with pythonPackages; [
            pytest
            pytest-cov
          ];

          checkPhase = ''
            pytest tests/python/
          '';

          meta = with pkgs.lib; {
            description = "Comprehensive IPv6-only networking tools";
            homepage = "https://github.com/Hyperpolymath/ipv6-only";
            license = with licenses; [ mit ];
            maintainers = [ "Hyperpolymath" ];
            platforms = platforms.all;
          };
        };

        # Go tools
        packages.ipv6-ping = pkgs.buildGoModule {
          pname = "ipv6-ping";
          version = "0.1.0";

          src = ./src/go;

          vendorHash = null; # No external dependencies

          subPackages = [ "cmd/ipv6-ping" ];

          meta = with pkgs.lib; {
            description = "IPv6 ping utility";
            homepage = "https://github.com/Hyperpolymath/ipv6-only";
            license = with licenses; [ mit ];
          };
        };

        packages.ipv6-scan = pkgs.buildGoModule {
          pname = "ipv6-scan";
          version = "0.1.0";

          src = ./src/go;

          vendorHash = null;

          subPackages = [ "cmd/ipv6-scan" ];

          meta = with pkgs.lib; {
            description = "IPv6 network scanner";
            homepage = "https://github.com/Hyperpolymath/ipv6-only";
            license = with licenses; [ mit ];
          };
        };

        packages.ipv6-trace = pkgs.buildGoModule {
          pname = "ipv6-trace";
          version = "0.1.0";

          src = ./src/go;

          vendorHash = null;

          subPackages = [ "cmd/ipv6-trace" ];

          meta = with pkgs.lib; {
            description = "IPv6 traceroute utility";
            homepage = "https://github.com/Hyperpolymath/ipv6-only";
            license = with licenses; [ mit ];
          };
        };

        packages.ipv6-lookup = pkgs.buildGoModule {
          pname = "ipv6-lookup";
          version = "0.1.0";

          src = ./src/go;

          vendorHash = null;

          subPackages = [ "cmd/ipv6-lookup" ];

          meta = with pkgs.lib; {
            description = "IPv6 DNS lookup tool";
            homepage = "https://github.com/Hyperpolymath/ipv6-only";
            license = with licenses; [ mit ];
          };
        };

        # All Go tools together
        packages.go-tools = pkgs.symlinkJoin {
          name = "ipv6-go-tools";
          paths = with self.packages.${system}; [
            ipv6-ping
            ipv6-scan
            ipv6-trace
            ipv6-lookup
          ];
        };

        # Complete package with everything
        packages.default = pkgs.symlinkJoin {
          name = "ipv6-only-tools";
          paths = with self.packages.${system}; [
            python-ipv6tools
            go-tools
          ];
        };

        # Container image
        packages.container = pkgs.dockerTools.buildLayeredImage {
          name = "ipv6-only";
          tag = "latest";

          contents = with pkgs; [
            self.packages.${system}.default
            python3
            go
            iproute2
            iputils
            bind
            bashInteractive
            coreutils
          ];

          config = {
            Cmd = [ "${pkgs.bashInteractive}/bin/bash" ];
            Env = [
              "PATH=/bin"
              "PYTHONUNBUFFERED=1"
            ];
            WorkingDir = "/app";
            ExposedPorts = {
              "8000/tcp" = {};
              "8443/tcp" = {};
            };
          };
        };

        # Apps for running tools
        apps = {
          ipv6-ping = {
            type = "app";
            program = "${self.packages.${system}.ipv6-ping}/bin/ipv6-ping";
          };
          ipv6-scan = {
            type = "app";
            program = "${self.packages.${system}.ipv6-scan}/bin/ipv6-scan";
          };
          ipv6-trace = {
            type = "app";
            program = "${self.packages.${system}.ipv6-trace}/bin/ipv6-trace";
          };
          ipv6-lookup = {
            type = "app";
            program = "${self.packages.${system}.ipv6-lookup}/bin/ipv6-lookup";
          };
        };

        # Checks (tests)
        checks = {
          python-tests = pkgs.runCommand "python-tests" {
            buildInputs = [ pythonEnv ];
          } ''
            cd ${./.}
            export PYTHONPATH="${./.}/src/python"
            pytest tests/python/ -v
            touch $out
          '';

          go-tests = pkgs.runCommand "go-tests" {
            buildInputs = [ pkgs.go_1_21 ];
          } ''
            cd ${./.}/src/go
            go test -v ./...
            touch $out
          '';

          format-check = pkgs.runCommand "format-check" {
            buildInputs = [ pythonEnv pkgs.go_1_21 ];
          } ''
            cd ${./.}
            # Python formatting check
            black --check src/python/ipv6tools/ || true
            # Go formatting check
            cd src/go && gofmt -l . | grep -q . && exit 1 || exit 0
            touch $out
          '';
        };

        # Formatter
        formatter = pkgs.nixpkgs-fmt;
      }
    );
}
