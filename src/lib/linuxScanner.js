/**
 * Linux scanner implementation - placeholder
 * Future implementation would use SANE through node bindings
 */

/**
 * List all available scanners
 * @returns {Promise<string[]>} Array of scanner names
 */
async function listScanners() {
    // Placeholder - would need SANE bindings
    return ['Scanner 1', 'Scanner 2'];
}

/**
 * Scan an image and return the file path
 * @returns {Promise<string|null>} Path to scanned image or null if cancelled
 */
async function scanImage() {
    // Placeholder - would need SANE bindings
    return null;
}

module.exports = {
    listScanners,
    scanImage
};
