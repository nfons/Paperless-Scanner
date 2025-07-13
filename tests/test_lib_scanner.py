import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os
from PIL import Image
import requests
from io import BytesIO

# Import the functions to test
from lib.scanner import list_scanners, scan_image, upload_to_paperlessngx


class TestLibScanner(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up any temporary files
        if os.path.exists('tmp.jpg'):
            os.remove('tmp.jpg')
    
    @patch('lib.scanner.win32com.client.Dispatch')
    def test_list_scanners_success(self, mock_dispatch):
        """Test list_scanners function with successful scanner detection."""
        # Mock the WIA DeviceManager
        mock_wia = Mock()
        mock_devices = Mock()
        
        # Create mock device infos
        mock_device1 = Mock()
        mock_device1.Type = 1  # Scanner type
        mock_device1.Properties.return_value.Value = "HP Scanner"
        
        mock_device2 = Mock()
        mock_device2.Type = 2  # Non-scanner type
        mock_device2.Properties.return_value.Value = "USB Camera"
        
        mock_device3 = Mock()
        mock_device3.Type = 1  # Scanner type
        mock_device3.Properties.return_value.Value = "Canon Scanner"
        
        mock_devices.__iter__ = Mock(return_value=iter([mock_device1, mock_device2, mock_device3]))
        mock_wia.DeviceInfos = mock_devices
        
        mock_dispatch.return_value = mock_wia
        
        # Call the function
        result = list_scanners()
        
        # Assertions
        self.assertEqual(result, ["HP Scanner", "Canon Scanner"])
        mock_dispatch.assert_called_once_with("WIA.DeviceManager")
    
    @patch('lib.scanner.win32com.client.Dispatch')
    def test_list_scanners_no_scanners(self, mock_dispatch):
        """Test list_scanners function when no scanners are found."""
        # Mock the WIA DeviceManager
        mock_wia = Mock()
        mock_devices = Mock()
        
        # Create mock device infos with no scanners
        mock_device1 = Mock()
        mock_device1.Type = 2  # Non-scanner type
        mock_device1.Properties.return_value.Value = "USB Camera"
        
        mock_device2 = Mock()
        mock_device2.Type = 3  # Non-scanner type
        mock_device2.Properties.return_value.Value = "Printer"
        
        mock_devices.__iter__ = Mock(return_value=iter([mock_device1, mock_device2]))
        mock_wia.DeviceInfos = mock_devices
        
        mock_dispatch.return_value = mock_wia
        
        # Call the function
        result = list_scanners()
        
        # Assertions
        self.assertEqual(result, [])
    
    @patch('lib.scanner.win32com.client.Dispatch')
    def test_list_scanners_exception(self, mock_dispatch):
        """Test list_scanners function when an exception occurs."""
        mock_dispatch.side_effect = Exception("WIA not available")
        
        # Call the function and expect an exception
        with self.assertRaises(Exception):
            list_scanners()
    
    @patch('lib.scanner.win32com.client.Dispatch')
    @patch('lib.scanner.Image.open')
    def test_scan_image_success(self, mock_image_open, mock_dispatch):
        """Test scan_image function with successful scan."""
        # Mock the WIA CommonDialog
        mock_wia = Mock()
        mock_wia_image = Mock()
        mock_wia.ShowAcquireImage.return_value = mock_wia_image
        
        mock_dispatch.return_value = mock_wia
        
        # Mock PIL Image
        mock_pil_image = Mock(spec=Image.Image)
        mock_image_open.return_value = mock_pil_image
        
        # Call the function
        result = scan_image()
        
        # Assertions
        self.assertEqual(result, mock_pil_image)
        mock_dispatch.assert_called_once_with("WIA.CommonDialog")
        mock_wia.ShowAcquireImage.assert_called_once()
        mock_wia_image.SaveFile.assert_called_once_with('tmp.jpg')
        mock_image_open.assert_called_once_with('tmp.jpg')
    
    @patch('lib.scanner.win32com.client.Dispatch')
    def test_scan_image_cancelled(self, mock_dispatch):
        """Test scan_image function when user cancels the scan."""
        # Mock the WIA CommonDialog
        mock_wia = Mock()
        mock_wia.ShowAcquireImage.return_value = None
        
        mock_dispatch.return_value = mock_wia
        
        # Call the function
        result = scan_image()
        
        # Assertions
        self.assertIsNone(result)
        mock_dispatch.assert_called_once_with("WIA.CommonDialog")
        mock_wia.ShowAcquireImage.assert_called_once()
    
    @patch('lib.scanner.win32com.client.Dispatch')
    def test_scan_image_exception(self, mock_dispatch):
        """Test scan_image function when an exception occurs."""
        mock_dispatch.side_effect = Exception("WIA not available")
        
        # Call the function and expect an exception
        with self.assertRaises(Exception):
            scan_image()
    
    @patch('lib.scanner.requests.post')
    def test_upload_to_paperlessngx_success(self, mock_post):
        """Test upload_to_paperlessngx function with successful upload."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "title": "test_document"}
        mock_post.return_value = mock_response
        
        # Create a temporary file for testing
        test_file_path = os.path.join(self.temp_dir, "test_document.pdf")
        with open(test_file_path, 'w') as f:
            f.write("test content")
        
        # Call the function
        success, status_code, response_data = upload_to_paperlessngx(
            test_file_path, 
            "http://localhost:8010", 
            "test_token"
        )
        
        # Assertions
        self.assertTrue(success)
        self.assertIsNone(status_code)
        self.assertIsNone(response_data)
        mock_post.assert_called_once()
        
        # Check the call arguments
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "http://localhost:8010/api/documents/post_document/")
        self.assertEqual(call_args[1]['headers'], {"Authorization": "Token test_token"})
        self.assertIn('document', call_args[1]['files'])
        self.assertEqual(call_args[1]['data'], {})
    
    @patch('lib.scanner.requests.post')
    def test_upload_to_paperlessngx_with_filename(self, mock_post):
        """Test upload_to_paperlessngx function with filename parameter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "title": "test_document"}
        mock_post.return_value = mock_response
        
        # Create a temporary file for testing
        test_file_path = os.path.join(self.temp_dir, "test_document.pdf")
        with open(test_file_path, 'w') as f:
            f.write("test content")
        
        # Call the function with filename
        success, status_code, response_data = upload_to_paperlessngx(
            test_file_path, 
            "http://localhost:8010", 
            "test_token",
            filename="test_document.pdf"
        )
        
        # Assertions
        self.assertTrue(success)
        self.assertIsNone(status_code)
        self.assertIsNone(response_data)
        
        # Check that title was set correctly
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data'], {"title": "test_document"})
    
    @patch('lib.scanner.requests.post')
    def test_upload_to_paperlessngx_failure(self, mock_post):
        """Test upload_to_paperlessngx function with failed upload."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad request"}
        mock_post.return_value = mock_response
        
        # Create a temporary file for testing
        test_file_path = os.path.join(self.temp_dir, "test_document.pdf")
        with open(test_file_path, 'w') as f:
            f.write("test content")
        
        # Call the function
        success, status_code, response_data = upload_to_paperlessngx(
            test_file_path, 
            "http://localhost:8010", 
            "test_token"
        )
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(status_code, 400)
        self.assertEqual(response_data, {"error": "Bad request"})
    
    @patch('lib.scanner.requests.post')
    def test_upload_to_paperlessngx_network_error(self, mock_post):
        """Test upload_to_paperlessngx function with network error."""
        # Mock network error
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        # Create a temporary file for testing
        test_file_path = os.path.join(self.temp_dir, "test_document.pdf")
        with open(test_file_path, 'w') as f:
            f.write("test content")
        
        # Call the function and expect an exception
        with self.assertRaises(requests.exceptions.RequestException):
            upload_to_paperlessngx(
                test_file_path, 
                "http://localhost:8010", 
                "test_token"
            )
    
    def test_upload_to_paperlessngx_file_not_found(self):
        """Test upload_to_paperlessngx function with non-existent file."""
        # Call the function with non-existent file
        with self.assertRaises(FileNotFoundError):
            upload_to_paperlessngx(
                "non_existent_file.pdf", 
                "http://localhost:8010", 
                "test_token"
            )
    
    def test_upload_to_paperlessngx_filename_without_extension(self):
        """Test upload_to_paperlessngx function with filename that has no extension."""
        # Create a temporary file for testing
        test_file_path = os.path.join(self.temp_dir, "test_document")
        with open(test_file_path, 'w') as f:
            f.write("test content")
        
        with patch('lib.scanner.requests.post') as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 123, "title": "test_document"}
            mock_post.return_value = mock_response
            
            # Call the function with filename without extension
            success, status_code, response_data = upload_to_paperlessngx(
                test_file_path, 
                "http://localhost:8010", 
                "test_token",
                filename="test_document"
            )
            
            # Assertions
            self.assertTrue(success)
            
            # Check that title was set correctly (no extension to remove)
            call_args = mock_post.call_args
            self.assertEqual(call_args[1]['data'], {"title": "test_document"})


if __name__ == '__main__':
    unittest.main() 