# pylint: disable=E1101, C0301, W0311, C0303, W0718, E0401
# pylint: disable = no-name-in-module
from PIL import Image
import requests
import os

# SO this is a bit of a hack, but it works, I will just comment out the windows_scanner.py file when using debian based systems 
# and use the linux scanner.py file on those systems
# import lib.windows_scanner as scanclient
if os.name == 'nt':
    import lib.windows_scanner as scanclient
else:
    import lib.linux_scanner as scanclient

def list_scanners():
    return scanclient.list_scanners()

def scan_image():
    return scanclient.scan_image()
        

def upload_to_paperlessngx(file_path, api_url, api_token, filename=None):
    headers = {
        "Authorization": f"Token {api_token}"
    }
    files = {
        "document": open(file_path, "rb")
    }
    
    # Prepare data with filename if provided
    data = {}
    if filename:
        # Remove file extension for the title
        title = os.path.splitext(filename)[0]
        data["title"] = title
    
    response = requests.post(f"{api_url}/api/documents/post_document/", headers=headers, files=files, data=data)
    # close the file
    files["document"].close()
    if response.status_code == 200:
        print("Upload successful:", response.json())
        return True, None, None
    else:
        print("Upload failed:", response.status_code, response.json())
        return False,response.status_code, response.json()
        # close the file

# testing only
if __name__ == "__main__":
    print(list_scanners())