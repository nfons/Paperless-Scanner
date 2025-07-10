import win32com.client
from PIL import Image
import requests
import os
import io
import tempfile

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
        

def upload_to_paperlessngx(file_path, api_url, api_token):
    headers = {
        "Authorization": f"Token {api_token}"
    }
    files = {
        "document": open(file_path, "rb")
    }
    response = requests.post(f"{api_url}/api/documents/post_document/", headers=headers, files=files)
    if response.status_code == 200:
        print("Upload successful:", response.json())
        return True, None, None
    else:
        print("Upload failed:", response.status_code, response.json())
        return False,response.status_code, response.json()

# testing only
if __name__ == "__main__":
    print(list_scanners())