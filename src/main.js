const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const { listScanners, scanImage } = require('./lib/scanner');
const { uploadToPaperless } = require('./lib/paperless');
const { getRecommendedFilename } = require('./lib/ai');
const { loadConfig, saveConfig } = require('./lib/config');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        backgroundColor: '#f0f0f0'
    });

    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    // Uncomment for development
    // mainWindow.webContents.openDevTools();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// IPC Handlers

ipcMain.handle('list-scanners', async () => {
    try {
        const scanners = await listScanners();
        return { success: true, scanners };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('scan-document', async () => {
    try {
        const imagePath = await scanImage();
        if (!imagePath) {
            return { success: false, cancelled: true };
        }
        return { success: true, imagePath };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('get-filename-suggestion', async (event, imagePath) => {
    try {
        const config = await loadConfig();
        if (!config) {
            return { success: true, filename: '' };
        }
        const filename = await getRecommendedFilename(imagePath, config);
        return { success: true, filename };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('upload-to-paperless', async (event, filePath, filename) => {
    try {
        const config = await loadConfig();
        if (!config || !config.api_url || !config.api_token) {
            return {
                success: false,
                error: 'Paperless-ngx configuration missing. Please configure in Settings.'
            };
        }

        const result = await uploadToPaperless(
            filePath,
            config.api_url,
            config.api_token,
            filename
        );

        return result;
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('load-config', async () => {
    try {
        const config = await loadConfig();
        return { success: true, config: config || {} };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('save-config', async (event, config) => {
    try {
        const success = await saveConfig(config);
        return { success };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('select-file', async () => {
    try {
        const result = await dialog.showOpenDialog(mainWindow, {
            title: 'Select Document to Upload',
            properties: ['openFile'],
            filters: [
                { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'pdf'] },
                { name: 'All Files', extensions: ['*'] }
            ]
        });

        if (result.canceled) {
            return { success: false, cancelled: true };
        }

        return { success: true, filePath: result.filePaths[0] };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('cleanup-temp', async (event, filePath) => {
    try {
        if (filePath && filePath.includes('tmp_scan')) {
            await fs.unlink(filePath);
        }
    } catch (error) {
        console.error('Error cleaning up temp file:', error);
    }
});
