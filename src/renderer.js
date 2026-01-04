const { ipcRenderer } = require('electron');
const fs = require('fs');

// DOM Elements
const scannerSelect = document.getElementById('scannerSelect');
const refreshBtn = document.getElementById('refreshBtn');
const scanBtn = document.getElementById('scanBtn');
const uploadBtn = document.getElementById('uploadBtn');
const settingsBtn = document.getElementById('settingsBtn');
const exitBtn = document.getElementById('exitBtn');
const saveBtn = document.getElementById('saveBtn');
const filenameSection = document.getElementById('filenameSection');
const filenameInput = document.getElementById('filenameInput');
const imageContainer = document.getElementById('imageContainer');
const status = document.getElementById('status');
const settingsModal = document.getElementById('settingsModal');
const saveConfigBtn = document.getElementById('saveConfigBtn');
const cancelConfigBtn = document.getElementById('cancelConfigBtn');

// State
let currentImagePath = null;
let currentFilename = null;

// Initialize
async function init() {
    await refreshScanners();
    await loadConfigToUI();
    setupEventListeners();
}

// Setup Event Listeners
function setupEventListeners() {
    refreshBtn.addEventListener('click', refreshScanners);
    scanBtn.addEventListener('click', scanDocument);
    uploadBtn.addEventListener('click', uploadDocument);
    settingsBtn.addEventListener('click', openSettings);
    exitBtn.addEventListener('click', () => window.close());
    saveBtn.addEventListener('click', saveFilename);
    saveConfigBtn.addEventListener('click', saveConfiguration);
    cancelConfigBtn.addEventListener('click', closeSettings);

    // AI Provider radio buttons
    const aiProviderRadios = document.querySelectorAll('input[name="aiProvider"]');
    aiProviderRadios.forEach(radio => {
        radio.addEventListener('change', handleAIProviderChange);
    });
}

// Refresh Scanners
async function refreshScanners() {
    setStatus('Refreshing scanners...');
    const result = await ipcRenderer.invoke('list-scanners');

    if (result.success && result.scanners.length > 0) {
        scannerSelect.innerHTML = '';
        result.scanners.forEach(scanner => {
            const option = document.createElement('option');
            option.value = scanner;
            option.textContent = scanner;
            scannerSelect.appendChild(option);
        });
        setStatus(`Found ${result.scanners.length} scanner(s)`);
    } else {
        scannerSelect.innerHTML = '<option>No scanners found</option>';
        setStatus('No scanners detected');
    }
}

// Scan Document
async function scanDocument() {
    setStatus('Scanning document...');
    const result = await ipcRenderer.invoke('scan-document');

    if (result.success) {
        currentImagePath = result.imagePath;
        displayImage(result.imagePath);

        // Get AI filename suggestion
        setStatus('Getting filename suggestion...');
        const filenameResult = await ipcRenderer.invoke('get-filename-suggestion', result.imagePath);

        if (filenameResult.success && filenameResult.filename) {
            filenameInput.value = filenameResult.filename;
        } else {
            filenameInput.value = '';
        }

        filenameSection.style.display = 'flex';
        filenameInput.focus();
        uploadBtn.textContent = 'Upload to Paperless';
        setStatus('Document scanned successfully! Enter filename to save.');
    } else if (result.cancelled) {
        setStatus('Scan cancelled');
    } else {
        setStatus(`Scan error: ${result.error || 'Unknown error'}`);
        alert(`Error during scanning: ${result.error || 'Unknown error'}`);
    }
}

// Save Filename
function saveFilename() {
    let filename = filenameInput.value.trim();

    if (!filename) {
        alert('Please enter a filename');
        return;
    }

    // Add .jpg extension if not provided
    if (!filename.match(/\.(jpg|jpeg|png|bmp|tiff|pdf)$/i)) {
        filename += '.jpg';
    }

    currentFilename = filename;
    filenameSection.style.display = 'none';
    setStatus(`Document saved as '${filename}'`);
    alert(`Document saved as '${filename}'`);
}

// Upload Document
async function uploadDocument() {
    // If no scanned image, open file selector
    if (!currentImagePath || !fs.existsSync(currentImagePath)) {
        const result = await ipcRenderer.invoke('select-file');
        if (result.success) {
            currentImagePath = result.filePath;
        } else {
            return;
        }
    }

    setStatus('Uploading to Paperless...');
    const result = await ipcRenderer.invoke('upload-to-paperless', currentImagePath, currentFilename);

    if (result.success) {
        setStatus('Document uploaded successfully!');
        alert('Document uploaded to Paperless-ngx!');

        // Cleanup temp file
        await ipcRenderer.invoke('cleanup-temp', currentImagePath);

        // Reset state
        currentImagePath = null;
        currentFilename = null;
        imageContainer.innerHTML = '<p class="placeholder-text">No image scanned yet.<br>Click \'Scan Document\' to start.</p>';
        uploadBtn.textContent = 'Select Document';
    } else {
        setStatus('Upload failed');
        alert(`Error uploading document: ${result.response || result.error || 'Unknown error'}`);
    }
}

// Display Image
function displayImage(imagePath) {
    const img = document.createElement('img');
    img.src = imagePath;
    img.alt = 'Scanned document';
    imageContainer.innerHTML = '';
    imageContainer.appendChild(img);
}

// Settings Modal
function openSettings() {
    settingsModal.style.display = 'block';
}

function closeSettings() {
    settingsModal.style.display = 'none';
}

// Load Config to UI
async function loadConfigToUI() {
    const result = await ipcRenderer.invoke('load-config');
    if (result.success && result.config) {
        const config = result.config;

        document.getElementById('apiUrl').value = config.api_url || '';
        document.getElementById('apiToken').value = config.api_token || '';
        document.getElementById('openaiApiKey').value = config.openai_api_key || '';
        document.getElementById('geminiApiKey').value = config.gemini_api_key || '';

        // Set AI provider radio
        if (config.openai_api_key) {
            document.querySelector('input[name="aiProvider"][value="openai"]').checked = true;
        } else if (config.gemini_api_key) {
            document.querySelector('input[name="aiProvider"][value="gemini"]').checked = true;
        } else {
            document.querySelector('input[name="aiProvider"][value="none"]').checked = true;
        }

        handleAIProviderChange();
    }
}

// Handle AI Provider Change
function handleAIProviderChange() {
    const selectedProvider = document.querySelector('input[name="aiProvider"]:checked').value;
    const openaiGroup = document.getElementById('openaiGroup');
    const geminiGroup = document.getElementById('geminiGroup');

    if (selectedProvider === 'openai') {
        openaiGroup.style.display = 'block';
        geminiGroup.style.display = 'none';
    } else if (selectedProvider === 'gemini') {
        openaiGroup.style.display = 'none';
        geminiGroup.style.display = 'block';
    } else {
        openaiGroup.style.display = 'none';
        geminiGroup.style.display = 'none';
    }
}

// Save Configuration
async function saveConfiguration() {
    const selectedProvider = document.querySelector('input[name="aiProvider"]:checked').value;

    const config = {
        api_url: document.getElementById('apiUrl').value.trim(),
        api_token: document.getElementById('apiToken').value.trim()
    };

    // Add AI keys based on selected provider
    if (selectedProvider === 'openai') {
        const openaiKey = document.getElementById('openaiApiKey').value.trim();
        if (openaiKey) {
            config.openai_api_key = openaiKey;
        }
    } else if (selectedProvider === 'gemini') {
        const geminiKey = document.getElementById('geminiApiKey').value.trim();
        if (geminiKey) {
            config.gemini_api_key = geminiKey;
        }
    }

    const result = await ipcRenderer.invoke('save-config', config);

    if (result.success) {
        alert('Configuration saved successfully!');
        closeSettings();
    } else {
        alert(`Error saving configuration: ${result.error || 'Unknown error'}`);
    }
}

// Set Status
function setStatus(message) {
    status.textContent = message;
}

// Initialize app
init();
