from PIL import Image
import win32com.client

# Windows only functionality
# pylint: disable=E1101, C0301, W0311, C0303, W0718

def list_scanners():
        wia = win32com.client.Dispatch("WIA.DeviceManager")
        devices = wia.DeviceInfos
        scanners = []
        for device in devices:
            if device.Type == 1:  # 1 = Scanner
                scanners.append(device.Properties("Name").Value)
        return scanners

def scan_image():
    """Scan an image and return a PIL Image object"""
    wia = win32com.client.Dispatch("WIA.CommonDialog")
    wia_image = wia.ShowAcquireImage()
    
    if wia_image is None:
        return None

    temp_path = 'tmp.jpg'
    wia_image.SaveFile(temp_path)

    # Load with PIL
    pil_image = Image.open(temp_path)
    return pil_image