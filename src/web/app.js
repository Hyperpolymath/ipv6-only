/**
 * IPv6 Tools Web Application
 * UI logic and event handlers
 */

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Deactivate all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Activate corresponding button
    event.target.classList.add('active');
}

// Show result with animation
function showResult(elementId, content, type = 'info') {
    const resultDiv = document.getElementById(elementId);
    resultDiv.innerHTML = content;
    resultDiv.className = `result show ${type}`;
}

// Validate Address
function validateAddress() {
    const input = document.getElementById('validateInput').value.trim();

    if (!input) {
        showResult('validateResult', '<p>Please enter an IPv6 address</p>', 'error');
        return;
    }

    const isValid = IPv6Tools.isValidIPv6(input);

    if (isValid) {
        const compressed = IPv6Tools.compress(input);
        const expanded = IPv6Tools.expand(input);
        const type = IPv6Tools.getAddressType(input);

        const typeBadge = getTypeBadge(type);

        const content = `
            <h4>✓ Valid IPv6 Address ${typeBadge}</h4>
            <table>
                <tr><th>Format</th><th>Address</th></tr>
                <tr><td>Compressed</td><td>${compressed}</td></tr>
                <tr><td>Expanded</td><td>${expanded}</td></tr>
                <tr><td>Type</td><td>${type}</td></tr>
            </table>
        `;

        showResult('validateResult', content, 'success');
    } else {
        showResult('validateResult', '<h4>✗ Invalid IPv6 Address</h4><p>The provided address is not a valid IPv6 address.</p>', 'error');
    }
}

// Calculate Network
function calculateNetwork() {
    const input = document.getElementById('calcInput').value.trim();

    if (!input) {
        showResult('calcResult', '<p>Please enter a network in CIDR notation</p>', 'error');
        return;
    }

    try {
        const info = IPv6Tools.calculateNetwork(input);

        const content = `
            <h4>Network Information</h4>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Network</td><td>${info.network}</td></tr>
                <tr><td>Network Address</td><td>${info.networkAddress}</td></tr>
                <tr><td>Prefix Length</td><td>/${info.prefixLength}</td></tr>
                <tr><td>Number of Addresses</td><td>${info.numAddresses.toLocaleString ? info.numAddresses.toLocaleString() : info.numAddresses}</td></tr>
                <tr><td>Address Type</td><td>${info.addressType}</td></tr>
            </table>
        `;

        showResult('calcResult', content, 'info');
    } catch (error) {
        showResult('calcResult', `<h4>Error</h4><p>${error.message}</p>`, 'error');
    }
}

// Convert Address
function convertAddress() {
    const input = document.getElementById('convertInput').value.trim();

    if (!input) {
        showResult('convertResult', '<p>Please enter an IPv6 address</p>', 'error');
        return;
    }

    if (!IPv6Tools.isValidIPv6(input)) {
        showResult('convertResult', '<h4>✗ Invalid IPv6 Address</h4>', 'error');
        return;
    }

    try {
        const compressed = IPv6Tools.compress(input);
        const expanded = IPv6Tools.expand(input);
        const type = IPv6Tools.getAddressType(input);

        const content = `
            <h4>Address Conversions</h4>
            <table>
                <tr><th>Format</th><th>Value</th></tr>
                <tr><td>Original</td><td>${input}</td></tr>
                <tr><td>Compressed</td><td>${compressed}</td></tr>
                <tr><td>Expanded</td><td>${expanded}</td></tr>
                <tr><td>Type</td><td>${type}</td></tr>
            </table>
        `;

        showResult('convertResult', content, 'info');
    } catch (error) {
        showResult('convertResult', `<h4>Error</h4><p>${error.message}</p>`, 'error');
    }
}

// Generate Link-Local
function generateLinkLocal() {
    const address = IPv6Tools.generateLinkLocal();
    const type = IPv6Tools.getAddressType(address);

    const content = `
        <h4>Generated Link-Local Address</h4>
        <p style="font-size: 1.2rem; font-weight: bold;">${address}</p>
        <p>Type: ${type}</p>
        <button onclick="navigator.clipboard.writeText('${address}')">Copy to Clipboard</button>
    `;

    showResult('linkLocalResult', content, 'success');
}

// Generate ULA
function generateULA() {
    const address = IPv6Tools.generateULA();
    const type = IPv6Tools.getAddressType(address);

    const content = `
        <h4>Generated Unique Local Address (ULA)</h4>
        <p style="font-size: 1.2rem; font-weight: bold;">${address}</p>
        <p>Type: ${type}</p>
        <button onclick="navigator.clipboard.writeText('${address}')">Copy to Clipboard</button>
    `;

    showResult('ulaResult', content, 'success');
}

// Generate Random
function generateRandom() {
    const prefix = document.getElementById('prefixInput').value.trim();

    try {
        const address = IPv6Tools.generateRandom(prefix);
        const type = IPv6Tools.getAddressType(address);

        const content = `
            <h4>Generated Random Address</h4>
            <p style="font-size: 1.2rem; font-weight: bold;">${address}</p>
            <p>Prefix: ${prefix}</p>
            <p>Type: ${type}</p>
            <button onclick="navigator.clipboard.writeText('${address}')">Copy to Clipboard</button>
        `;

        showResult('randomResult', content, 'success');
    } catch (error) {
        showResult('randomResult', `<h4>Error</h4><p>${error.message}</p>`, 'error');
    }
}

// Generate from MAC
function generateFromMAC() {
    const mac = document.getElementById('macInput').value.trim();

    if (!mac) {
        showResult('macResult', '<p>Please enter a MAC address</p>', 'error');
        return;
    }

    try {
        const address = IPv6Tools.macToIPv6(mac);
        const type = IPv6Tools.getAddressType(address);

        const content = `
            <h4>Generated IPv6 from MAC (EUI-64)</h4>
            <p>MAC Address: ${mac}</p>
            <p style="font-size: 1.2rem; font-weight: bold;">${address}</p>
            <p>Type: ${type}</p>
            <button onclick="navigator.clipboard.writeText('${address}')">Copy to Clipboard</button>
        `;

        showResult('macResult', content, 'success');
    } catch (error) {
        showResult('macResult', `<h4>Error</h4><p>${error.message}</p>`, 'error');
    }
}

// Plan Subnets
function planSubnets() {
    const network = document.getElementById('subnetInput').value.trim();
    const count = parseInt(document.getElementById('subnetCount').value);

    if (!network) {
        showResult('subnetResult', '<p>Please enter a base network</p>', 'error');
        return;
    }

    if (isNaN(count) || count < 1) {
        showResult('subnetResult', '<p>Please enter a valid number of subnets</p>', 'error');
        return;
    }

    try {
        const subnets = IPv6Tools.divideNetwork(network, count);

        let tableRows = '';
        subnets.forEach((subnet, index) => {
            tableRows += `
                <tr>
                    <td>Subnet ${index + 1}</td>
                    <td>${subnet.network}</td>
                    <td>${subnet.networkAddress}</td>
                </tr>
            `;
        });

        const content = `
            <h4>Subnet Plan</h4>
            <p>Base Network: ${network}</p>
            <p>Number of Subnets: ${subnets.length}</p>
            <p>New Prefix Length: /${subnets[0].prefixLength}</p>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Network (CIDR)</th>
                        <th>Network Address</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        `;

        showResult('subnetResult', content, 'info');
    } catch (error) {
        showResult('subnetResult', `<h4>Error</h4><p>${error.message}</p>`, 'error');
    }
}

// Helper function to get type badge
function getTypeBadge(type) {
    const badges = {
        'Link-Local': '<span class="badge link-local">Link-Local</span>',
        'Global Unicast': '<span class="badge global">Global</span>',
        'Unique Local (ULA)': '<span class="badge ula">ULA</span>',
        'Multicast': '<span class="badge multicast">Multicast</span>',
        'Loopback': '<span class="badge">Loopback</span>',
    };

    return badges[type] || '';
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Enter key triggers validation/calculation on active tab
    if (event.key === 'Enter') {
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab) {
            const button = activeTab.querySelector('button');
            if (button) button.click();
        }
    }
});

console.log('IPv6 Tools Web Application loaded successfully');
