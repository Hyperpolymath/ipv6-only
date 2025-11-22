/**
 * IPv6 Tools Library - JavaScript Implementation
 * Provides IPv6 address manipulation and validation utilities
 */

const IPv6Tools = {
    /**
     * Validate IPv6 address format
     */
    isValidIPv6: function(address) {
        if (!address || typeof address !== 'string') return false;

        // Remove zone ID if present
        address = address.split('%')[0];

        // IPv6 regex pattern
        const ipv6Pattern = /^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+|::(ffff(:0{1,4})?:)?((25[0-5]|(2[0-4]|1?[0-9])?[0-9])\.){3}(25[0-5]|(2[0-4]|1?[0-9])?[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1?[0-9])?[0-9])\.){3}(25[0-5]|(2[0-4]|1?[0-9])?[0-9]))$/;

        return ipv6Pattern.test(address);
    },

    /**
     * Compress IPv6 address to shortest form
     */
    compress: function(address) {
        if (!this.isValidIPv6(address)) throw new Error('Invalid IPv6 address');

        const parts = address.split('%');
        let addr = parts[0];
        const zone = parts[1];

        // Expand first to normalize
        addr = this.expand(addr);

        // Split into groups
        let groups = addr.split(':');

        // Remove leading zeros from each group
        groups = groups.map(g => g.replace(/^0+/, '') || '0');

        // Find longest sequence of zeros
        let longestZeroSeq = {start: -1, length: 0};
        let currentZeroSeq = {start: -1, length: 0};

        for (let i = 0; i < groups.length; i++) {
            if (groups[i] === '0') {
                if (currentZeroSeq.start === -1) {
                    currentZeroSeq.start = i;
                    currentZeroSeq.length = 1;
                } else {
                    currentZeroSeq.length++;
                }

                if (currentZeroSeq.length > longestZeroSeq.length) {
                    longestZeroSeq = {...currentZeroSeq};
                }
            } else {
                currentZeroSeq = {start: -1, length: 0};
            }
        }

        // Replace longest zero sequence with ::
        if (longestZeroSeq.length > 1) {
            const before = groups.slice(0, longestZeroSeq.start);
            const after = groups.slice(longestZeroSeq.start + longestZeroSeq.length);

            if (before.length === 0 && after.length === 0) {
                addr = '::';
            } else if (before.length === 0) {
                addr = '::' + after.join(':');
            } else if (after.length === 0) {
                addr = before.join(':') + '::';
            } else {
                addr = before.join(':') + '::' + after.join(':');
            }
        } else {
            addr = groups.join(':');
        }

        return zone ? addr + '%' + zone : addr;
    },

    /**
     * Expand IPv6 address to full form
     */
    expand: function(address) {
        if (!this.isValidIPv6(address)) throw new Error('Invalid IPv6 address');

        const parts = address.split('%');
        let addr = parts[0];
        const zone = parts[1];

        // Handle :: expansion
        if (addr.includes('::')) {
            const sides = addr.split('::');
            const leftGroups = sides[0] ? sides[0].split(':') : [];
            const rightGroups = sides[1] ? sides[1].split(':') : [];
            const missingGroups = 8 - leftGroups.length - rightGroups.length;

            const middleGroups = Array(missingGroups).fill('0000');
            const allGroups = [...leftGroups, ...middleGroups, ...rightGroups];

            addr = allGroups.map(g => g.padStart(4, '0')).join(':');
        } else {
            addr = addr.split(':').map(g => g.padStart(4, '0')).join(':');
        }

        return zone ? addr + '%' + zone : addr;
    },

    /**
     * Get address type
     */
    getAddressType: function(address) {
        if (!this.isValidIPv6(address)) return 'Invalid';

        address = address.split('%')[0];
        const expanded = this.expand(address);
        const first16 = expanded.substring(0, 4);
        const first8 = first16.substring(0, 2);

        if (expanded === '0000:0000:0000:0000:0000:0000:0000:0001') {
            return 'Loopback';
        } else if (expanded === '0000:0000:0000:0000:0000:0000:0000:0000') {
            return 'Unspecified';
        } else if (first16.startsWith('fe80')) {
            return 'Link-Local';
        } else if (first8 === 'fc' || first8 === 'fd') {
            return 'Unique Local (ULA)';
        } else if (first8 === 'ff') {
            return 'Multicast';
        } else if (first8 >= '20' && first8 <= '3f') {
            return 'Global Unicast';
        } else {
            return 'Reserved';
        }
    },

    /**
     * Generate random IPv6 address
     */
    generateRandom: function(prefix = '2001:db8::/64') {
        const [network, prefixLen] = prefix.split('/');
        const prefixLength = parseInt(prefixLen) || 64;

        const hostBits = 128 - prefixLength;
        const hostGroups = Math.ceil(hostBits / 16);

        // Expand network address
        let base = this.expand(network);
        let baseGroups = base.split(':');

        // Replace host portion with random values
        const randomStart = 8 - hostGroups;
        for (let i = randomStart; i < 8; i++) {
            baseGroups[i] = Math.floor(Math.random() * 65536).toString(16).padStart(4, '0');
        }

        return this.compress(baseGroups.join(':'));
    },

    /**
     * Generate link-local address
     */
    generateLinkLocal: function() {
        const interfaceId = Array.from({length: 4}, () =>
            Math.floor(Math.random() * 65536).toString(16).padStart(4, '0')
        ).join(':');

        return this.compress('fe80::' + interfaceId);
    },

    /**
     * Generate Unique Local Address (ULA)
     */
    generateULA: function() {
        const globalId = Array.from({length: 10}, () =>
            Math.floor(Math.random() * 16).toString(16)
        ).join('');

        const subnetId = Math.floor(Math.random() * 65536).toString(16).padStart(4, '0');

        const interfaceId = Array.from({length: 4}, () =>
            Math.floor(Math.random() * 65536).toString(16).padStart(4, '0')
        ).join(':');

        const addr = `fd${globalId.substring(0, 2)}:${globalId.substring(2, 6)}:${globalId.substring(6, 10)}${subnetId}:${interfaceId}`;

        return this.compress(addr);
    },

    /**
     * Convert MAC address to IPv6 link-local using EUI-64
     */
    macToIPv6: function(mac) {
        // Clean MAC address
        mac = mac.replace(/[:-]/g, '').toLowerCase();

        if (mac.length !== 12) throw new Error('Invalid MAC address length');
        if (!/^[0-9a-f]+$/.test(mac)) throw new Error('Invalid MAC address format');

        // Insert fffe in the middle
        const eui64 = mac.substring(0, 6) + 'fffe' + mac.substring(6);

        // Flip universal/local bit (7th bit of first octet)
        let firstOctet = parseInt(eui64.substring(0, 2), 16);
        firstOctet ^= 0x02;

        const modifiedEui64 = firstOctet.toString(16).padStart(2, '0') + eui64.substring(2);

        // Format as IPv6 address
        const parts = [];
        for (let i = 0; i < 16; i += 4) {
            parts.push(modifiedEui64.substring(i, i + 4));
        }

        const addr = 'fe80::' + parts.join(':');

        return this.compress(addr);
    },

    /**
     * Calculate network information
     */
    calculateNetwork: function(cidr) {
        const [network, prefixLen] = cidr.split('/');
        const prefixLength = parseInt(prefixLen);

        if (!this.isValidIPv6(network)) throw new Error('Invalid network address');
        if (isNaN(prefixLength) || prefixLength < 0 || prefixLength > 128) {
            throw new Error('Invalid prefix length');
        }

        const expanded = this.expand(network);
        const groups = expanded.split(':').map(g => parseInt(g, 16));

        // Calculate network address (zero out host bits)
        const networkGroups = [...groups];
        const hostBits = 128 - prefixLength;
        const fullHostGroups = Math.floor(hostBits / 16);
        const partialBits = hostBits % 16;

        // Zero out full host groups
        for (let i = 8 - fullHostGroups; i < 8; i++) {
            networkGroups[i] = 0;
        }

        // Zero out partial bits
        if (partialBits > 0) {
            const maskGroup = 8 - fullHostGroups - 1;
            const mask = (0xFFFF << partialBits) & 0xFFFF;
            networkGroups[maskGroup] &= mask;
        }

        const networkAddr = this.compress(networkGroups.map(g => g.toString(16).padStart(4, '0')).join(':'));

        // Calculate number of addresses
        const numAddresses = hostBits <= 53 ? Math.pow(2, hostBits) : 'Too large (2^' + hostBits + ')';

        return {
            network: networkAddr + '/' + prefixLength,
            networkAddress: networkAddr,
            prefixLength: prefixLength,
            numAddresses: numAddresses,
            addressType: this.getAddressType(networkAddr)
        };
    },

    /**
     * Divide network into subnets
     */
    divideNetwork: function(cidr, numSubnets) {
        const [network, prefixLen] = cidr.split('/');
        const prefixLength = parseInt(prefixLen);

        const bitsNeeded = Math.ceil(Math.log2(numSubnets));
        const newPrefix = prefixLength + bitsNeeded;

        if (newPrefix > 128) throw new Error('Cannot divide into that many subnets');

        const subnets = [];
        const expanded = this.expand(network);
        const baseGroups = expanded.split(':').map(g => parseInt(g, 16));

        for (let i = 0; i < numSubnets; i++) {
            const subnetGroups = [...baseGroups];

            // Add subnet bits
            const subnetBitGroup = Math.floor((prefixLength + bitsNeeded - 1) / 16);
            const bitPosition = 16 - ((prefixLength + bitsNeeded) % 16 || 16);

            subnetGroups[subnetBitGroup] |= (i << bitPosition);

            const subnetAddr = this.compress(subnetGroups.map(g => g.toString(16).padStart(4, '0')).join(':'));

            subnets.push({
                network: subnetAddr + '/' + newPrefix,
                networkAddress: subnetAddr,
                prefixLength: newPrefix
            });
        }

        return subnets;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IPv6Tools;
}
