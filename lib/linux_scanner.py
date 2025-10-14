import platform
from PIL import Image

def list_scanners():
    system = platform.system().lower()
    if system == 'darwin' or system == 'linux':
        try:
            from pyinsane2 import scanners # hiding it here to avoid import errors on Windows
            devices = scanners.get_devices()
            return [dev.name for dev in devices]
        except Exception as e:
            print(f"Error listing scanners: {e}")
            return []
    else:
        return ["Scanner 1", "Scanner 2"]

def scan_image():
    system = platform.system().lower()
    if system == 'darwin' or system == 'linux':
        try:
            from pyinsane2 import scanners
            devices = scanners.get_devices()
            if not devices:
                print("No scanners found")
                return None
            scanner = devices[0]  # Use the first scanner found
            scan_session = scanner.scan(multiple=False)
            while True:
                try:
                    scan_session.scan.read()
                except EOFError:
                    break
            image = scan_session.images[0]
            pil_image = Image.fromarray(image)
            pil_image.save('tmp.jpg')
            return pil_image
        except Exception as e:
            print(f"Error scanning image: {e}")
            return None
    else:
        return None
