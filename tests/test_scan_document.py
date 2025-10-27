import os
import unittest
from unittest.mock import patch, Mock

import app


class DummyVar:
    def __init__(self):
        self.value = None

    def set(self, v):
        self.value = v

    def get(self):
        return self.value


class TestScanDocument(unittest.TestCase):
    def setUp(self):
        # Create a bare instance without invoking __init__
        self.instance = app.PaperlessScanApp.__new__(app.PaperlessScanApp)

        # Minimal attributes used by scan_document
        self.instance.status_label = Mock()
        self.instance.status_label.config = Mock()
        self.instance.root = Mock()
        self.instance.root.update = Mock()
        self.instance.filename_frame = Mock()
        self.instance.filename_frame.pack = Mock()
        self.instance.filename_var = DummyVar()
        self.instance.filename_entry = Mock()
        self.instance.filename_entry.focus = Mock()
        self.instance.upload_button = Mock()
        self.instance.upload_button.config = Mock()
        # Ensure cleanup won't error
        if os.path.exists('tmp.jpg'):
            os.remove('tmp.jpg')

    def tearDown(self):
        if os.path.exists('tmp.jpg'):
            os.remove('tmp.jpg')

    @patch('app.scan_image')
    @patch('app.get_recommended_filename_from_pil_image')
    def test_scan_success(self, mock_getname, mock_scan):
        # Return a simple dummy image object from scan
        img = object()
        mock_scan.return_value = img
        mock_getname.return_value = 'recommended_name'

        # Ensure no API keys so openai path not used
        self.instance.openai_api_key = None
        self.instance.gemini_api_key = None

        # Provide a mock display_image_object so scan_document won't raise
        self.instance.display_image_object = Mock()

        # Call method
        self.instance.scan_document()

        # display_image_object should be called (method on instance was mocked)
        self.instance.display_image_object.assert_called_once_with(img)
        self.assertEqual(self.instance.scanned_image, img)
        # filename_frame.pack called
        self.instance.filename_frame.pack.assert_called()
        # filename_var set (empty string expected because no api keys)
        self.assertEqual(self.instance.filename_var.get(), "")
        # scanned_image_path set to tmp.jpg
        self.assertEqual(self.instance.scanned_image_path, 'tmp.jpg')
        # upload button enabled
        self.instance.upload_button.config.assert_called_with(state='normal')
        # status_label updated to success message
        self.instance.status_label.config.assert_called_with(text="Document scanned successfully! Enter filename to save.")

    @patch('app.scan_image')
    @patch('app.messagebox.showinfo')
    def test_scan_cancelled(self, mock_showinfo, mock_scan):
        mock_scan.return_value = None

        self.instance.scan_document()

        # status_label should be set to cancelled text
        self.instance.status_label.config.assert_called_with(text="Scan cancelled or failed")
        mock_showinfo.assert_called_once_with("Scan Cancelled", "Scan was cancelled or failed")

    @patch('app.scan_image')
    @patch('app.messagebox.showerror')
    def test_scan_exception(self, mock_showerror, mock_scan):
        mock_scan.side_effect = Exception('boom')

        self.instance.scan_document()

        # status_label should reflect the exception
        self.instance.status_label.config.assert_called()
        # messagebox.showerror called
        mock_showerror.assert_called()


if __name__ == '__main__':
    unittest.main()
