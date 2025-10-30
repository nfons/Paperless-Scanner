import os
import tempfile
import importlib
import types
import unittest
from unittest.mock import patch, Mock

import lib.scanner as scanner


class TestLibScanner(unittest.TestCase):
    def setUp(self):
        self.api_url = 'http://localhost:8000'
        self.api_token = 'token123' # clearly fake

    def test_upload_success_closes_file_and_returns_true(self):
        # create a temp file
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        # write something
        with open(path, 'wb') as f:
            f.write(b'hello')

        captured = {}

        def fake_post(url, headers=None, files=None, data=None):
            # capture what was passed
            captured['url'] = url
            captured['headers'] = headers
            captured['files'] = files
            captured['data'] = data
            # return a response-like object
            resp = Mock()
            resp.status_code = 200
            resp.json = lambda: {'status': 'ok'}
            return resp

        with patch('lib.scanner.requests.post', side_effect=fake_post) as mock_post:
            ok, code, resp = scanner.upload_to_paperlessngx(path, self.api_url, self.api_token, filename='mydoc.pdf')

        # Should return success
        self.assertTrue(ok)
        self.assertIsNone(code)
        self.assertIsNone(resp)

        # Ensure post was called and url formed correctly
        self.assertEqual(captured['url'], f'{self.api_url}/api/documents/post_document/')
        # Data should include title without extension
        self.assertEqual(captured['data'].get('title'), 'mydoc')

        # The file object used should be closed by the function
        fileobj = captured['files']['document']
        self.assertTrue(fileobj.closed)

        os.remove(path)

    def test_upload_failure_returns_false_and_response(self):
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        with open(path, 'wb') as f:
            f.write(b'content')

        def fake_post(url, headers=None, files=None, data=None):
            resp = Mock()
            resp.status_code = 400
            resp.json = lambda: {'error': 'bad'}
            return resp

        with patch('lib.scanner.requests.post', side_effect=fake_post):
            ok, code, resp = scanner.upload_to_paperlessngx(path, self.api_url, self.api_token, filename='file.txt')

        self.assertFalse(ok)
        self.assertEqual(code, 400)
        self.assertEqual(resp, {'error': 'bad'})

        os.remove(path)

    def test_list_scanners_delegates_to_scanclient(self):
        # patch the scanclient on the module to a dummy object
        dummy = types.SimpleNamespace()
        dummy.list_scanners = lambda: ['S1', 'S2']
        orig = scanner.scanclient
        try:
            scanner.scanclient = dummy
            vals = scanner.list_scanners()
            self.assertEqual(vals, ['S1', 'S2'])
        finally:
            scanner.scanclient = orig

    def test_scan_image_delegates_to_scanclient(self):
        dummy = types.SimpleNamespace()
        dummy.scan_image = lambda: 'IMG'
        orig = scanner.scanclient
        try:
            scanner.scanclient = dummy
            img = scanner.scan_image()
            self.assertEqual(img, 'IMG')
        finally:
            scanner.scanclient = orig


if __name__ == '__main__':
    unittest.main()
