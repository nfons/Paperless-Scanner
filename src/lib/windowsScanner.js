const edge = require('electron-edge-js');
const fs = require('fs').promises;
const path = require('path');

// C# code to interface with WIA
const listScannersCS = `
    #r "System.Runtime.InteropServices.dll"
    using System;
    using System.Collections.Generic;
    using System.Threading.Tasks;

    public class Startup
    {
        public async Task<object> Invoke(object input)
        {
            try
            {
                Type wiaDeviceManagerType = Type.GetTypeFromProgID("WIA.DeviceManager");
                dynamic wia = Activator.CreateInstance(wiaDeviceManagerType);
                dynamic devices = wia.DeviceInfos;

                List<string> scanners = new List<string>();

                foreach (dynamic device in devices)
                {
                    if (device.Type == 1) // 1 = Scanner
                    {
                        scanners.Add(device.Properties["Name"].Value.ToString());
                    }
                }

                return scanners.ToArray();
            }
            catch (Exception ex)
            {
                return new string[] { };
            }
        }
    }
`;

const scanImageCS = `
    #r "System.Runtime.InteropServices.dll"
    using System;
    using System.Threading.Tasks;
    using System.IO;

    public class Startup
    {
        public async Task<object> Invoke(object input)
        {
            try
            {
                Type wiaCommonDialogType = Type.GetTypeFromProgID("WIA.CommonDialog");
                dynamic wia = Activator.CreateInstance(wiaCommonDialogType);
                dynamic wiaImage = wia.ShowAcquireImage();

                if (wiaImage == null)
                {
                    return null;
                }

                string tempPath = Path.Combine(Path.GetTempPath(), "tmp_scan.jpg");
                wiaImage.SaveFile(tempPath);

                return tempPath;
            }
            catch (Exception ex)
            {
                return null;
            }
        }
    }
`;

// Create Edge.js functions
let listScannersFunc = null;
let scanImageFunc = null;

try {
   listScannersFunc = edge.func(listScannersCS);
   scanImageFunc = edge.func(scanImageCS);
} catch (error) {
    console.error('Failed to initialize scanner functions:', error);
}

/**
 * List all available scanners
 * @returns {Promise<string[]>} Array of scanner names
 */
async function listScanners() {
    if (!listScannersFunc) {
        throw new Error('Scanner functions not initialized. Make sure you are on Windows.');
    }

    try {
        let scanners = undefined;
        await listScannersFunc(null, (err, result) => {
            scanners = result;
        });
        return scanners || [];
    } catch (error) {
        console.error('Error listing scanners:', error);
        return [];
    }
}

/**
 * Scan an image and return the file path
 * @returns {Promise<string|null>} Path to scanned image or null if cancelled
 */
async function scanImage() {
    if (!scanImageFunc) {
        throw new Error('Scanner functions not initialized. Make sure you are on Windows.');
    }

    try {
        let tempPath = undefined; 
        await scanImageFunc(null, (err, result) => {
            tempPath = result;
        });
        return tempPath;
    } catch (error) {
        console.error('Error scanning image:', error);
        return null;
    }
}

module.exports = {
    listScanners,
    scanImage
};
