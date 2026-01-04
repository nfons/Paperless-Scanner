const os = require('os');

// Import the appropriate scanner module based on platform
let scannerModule;

if (os.platform() === 'win32') {
    scannerModule = require('./windowsScanner');
} else if (os.platform() === 'linux') {
    scannerModule = require('./linuxScanner');
} else {
    // Fallback for unsupported platforms
    scannerModule = {
        listScanners: async () => [],
        scanImage: async () => null
    };
}

/**
 * List all available scanners
 * @returns {Promise<string[]>} Array of scanner names
 */
async function listScanners() {
    return await scannerModule.listScanners();
}

/**
 * Scan an image and return the file path
 * @returns {Promise<string|null>} Path to scanned image or null if cancelled
 */
async function scanImage() {
    return await scannerModule.scanImage();
}

module.exports = {
    listScanners,
    scanImage
};
