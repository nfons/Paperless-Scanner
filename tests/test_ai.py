import unittest
from unittest.mock import Mock, patch
import io
import os
import tempfile
from PIL import Image

import lib.ai as ai

class TestAI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_key_123"
        # Create a small test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        # Create a temporary file for testing
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.jpg')
        self.test_image.save(self.temp_path)

    def tearDown(self):
        # Clean up temp files
        os.close(self.temp_fd)
        os.remove(self.temp_path)

    def test_pil_to_bytes_conversion(self):
        """Test PIL_to_bytes converts image to JPEG bytes correctly"""
        # Convert test image to bytes
        img_bytes = ai.PIL_to_bytes(self.test_image)
        
        # Should be bytes
        self.assertIsInstance(img_bytes, bytes)
        
        # Should be valid JPEG data
        img = Image.open(io.BytesIO(img_bytes))
        self.assertEqual(img.format, 'JPEG')

    @patch('openai.OpenAI')
    def test_apirequest_success(self, mock_openai):
        """Test successful OpenAI API request with proper response parsing"""
        # Mock the OpenAI response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_completion = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices = [
            Mock(message=Mock(content=" Test Document 2025.pdf "))
        ]

        # Call apirequest
        result = ai.apirequest(self.api_key, b'test_image_data')

        # Verify the result is cleaned properly
        self.assertEqual(result, 'Test_Document_2025pdf')

        # Verify API was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs['model'], 'gpt-4o-mini')
        self.assertEqual(call_kwargs['max_tokens'], 50)
        self.assertAlmostEqual(call_kwargs['temperature'], 0.3)

    @patch('google.genai.types.Part.from_bytes')
    @patch('google.genai.Client')
    def test_gemini_filename_recommendation(self, mock_client_class, mock_from_bytes):
        """Test Gemini-based filename recommendation"""
        # Setup mock response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock streaming response
        mock_client.models.generate_content_stream.return_value = [
            Mock(text="recommended_filename")
        ]
        
        result = ai.get_recommended_filename_from_pil_image_gemini(
            self.test_image, 
            self.api_key
        )
        
        self.assertEqual(result, "recommended_filename")
        mock_client_class.assert_called_once_with(api_key=self.api_key)
        mock_from_bytes.assert_called_once()

    @patch('lib.ai.apirequest')
    def test_get_recommended_filename_handles_errors(self, mock_apirequest):
        """Test error handling in get_recommended_filename"""
        # Make apirequest raise an exception
        mock_apirequest.side_effect = Exception("API Error")
        
        # Should handle error and return None
        result = ai.get_recommended_filename(self.temp_path, self.api_key)
        self.assertIsNone(result)

    @patch('lib.ai.apirequest')
    def test_get_recommended_filename_from_pil_image(self, mock_apirequest):
        """Test get_recommended_filename_from_pil_image with success and failure"""
        # Test successful case
        mock_apirequest.return_value = "test_document"
        result = ai.get_recommended_filename_from_pil_image(self.test_image, self.api_key)
        self.assertEqual(result, "test_document")
        
        # Test error case
        mock_apirequest.side_effect = Exception("API Error")
        result = ai.get_recommended_filename_from_pil_image(self.test_image, self.api_key)
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()