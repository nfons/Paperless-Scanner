const fs = require('fs').promises;
const yaml = require('js-yaml');
const path = require('path');

const CONFIG_FILE = 'config.yaml';

/**
 * Load configuration from config.yaml
 * @returns {Promise<Object|null>} Configuration object or null if not found
 */
async function loadConfig() {
    try {
        const configPath = path.join(process.cwd(), CONFIG_FILE);
        const fileContents = await fs.readFile(configPath, 'utf8');
        const config = yaml.load(fileContents);
        return config || {};
    } catch (error) {
        if (error.code === 'ENOENT') {
            console.log('Config file not found');
            return null;
        }
        console.error('Error loading config:', error);
        return null;
    }
}

/**
 * Save configuration to config.yaml
 * @param {Object} config - Configuration object to save
 * @returns {Promise<boolean>} True if successful, false otherwise
 */
async function saveConfig(config) {
    try {
        const configPath = path.join(process.cwd(), CONFIG_FILE);
        const yamlStr = yaml.dump(config);
        await fs.writeFile(configPath, yamlStr, 'utf8');
        return true;
    } catch (error) {
        console.error('Error saving config:', error);
        return false;
    }
}

/**
 * Get a specific config value
 * @param {string} key - Configuration key
 * @returns {Promise<any>} Configuration value or null
 */
async function getConfigValue(key) {
    const config = await loadConfig();
    return config ? config[key] : null;
}

/**
 * Set a specific config value
 * @param {string} key - Configuration key
 * @param {any} value - Value to set
 * @returns {Promise<boolean>} True if successful
 */
async function setConfigValue(key, value) {
    let config = await loadConfig();
    if (!config) {
        config = {};
    }
    config[key] = value;
    return await saveConfig(config);
}

module.exports = {
    loadConfig,
    saveConfig,
    getConfigValue,
    setConfigValue
};
