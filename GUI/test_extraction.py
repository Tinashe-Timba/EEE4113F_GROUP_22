import unittest
from unittest.mock import patch, MagicMock
import datetime
from GUI_FINAL import extract_date  

class TestExtractDate(unittest.TestCase):
    def test_extract_date_valid_data(self):
        filename = 'test.jpg'
        
        with patch('PIL.Image.open', MagicMock()) as mock_img:
            mock_img.return_value.__enter__.return_value._getexif.return_value = {36868: '2020:01:01 00:00:00'}
            # Execute
            result = extract_date(filename)
            # Verify
            self.assertEqual(result, datetime.date(2020, 1, 1))

    def test_extract_date_no_exif(self):
        filename = 'test.jpg'
        with patch('PIL.Image.open', MagicMock()) as mock_img:
            mock_img.return_value.__enter__.return_value._getexif.return_value = None
            # Execute
            result = extract_date(filename)
            # Verify
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
