import unittest
import numpy as np
from ml.preprocessing import DataPreprocessor
from config import Config

class TestDataPreprocessor(unittest.TestCase):
    
    def setUp(self):
        self.config = Config()
        self.preprocessor = DataPreprocessor()
    
    def test_add_data(self):
        """Test adding data to buffer"""
        # Add single data point
        sensor_data = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
        self.preprocessor.add_data(sensor_data)
        
        self.assertEqual(len(self.preprocessor.data_buffer), 1)
        self.assertEqual(self.preprocessor.data_buffer[0], sensor_data)
    
    def test_window_size_limit(self):
        """Test that buffer maintains correct window size"""
        # Add more data points than window size
        for i in range(self.config.WINDOW_SIZE + 10):
            sensor_data = (float(i), float(i+1), float(i+2), 
                          float(i+3), float(i+4), float(i+5))
            self.preprocessor.add_data(sensor_data)
        
        # Buffer should not exceed window size
        self.assertEqual(len(self.preprocessor.data_buffer), self.config.WINDOW_SIZE)
        
        # First item should be the correct one (after removing oldest)
        expected_first = (10.0, 11.0, 12.0, 13.0, 14.0, 15.0)
        self.assertEqual(self.preprocessor.data_buffer[0], expected_first)
    
    def test_get_window(self):
        """Test getting data window"""
        # Add less than window size data
        for i in range(self.config.WINDOW_SIZE - 10):
            sensor_data = (float(i), float(i+1), float(i+2), 
                          float(i+3), float(i+4), float(i+5))
            self.preprocessor.add_data(sensor_data)
        
        # Should return None when not enough data
        window = self.preprocessor.get_window()
        self.assertIsNone(window)
        
        # Add enough data to fill window
        for i in range(10):
            sensor_data = (float(i+40), float(i+41), float(i+42), 
                          float(i+43), float(i+44), float(i+45))
            self.preprocessor.add_data(sensor_data)
        
        # Should return window when enough data
        window = self.preprocessor.get_window()
        self.assertIsNotNone(window)
        self.assertEqual(window.shape, (self.config.WINDOW_SIZE, self.config.FEATURES))
    
    def test_normalize_data(self):
        """Test data normalization"""
        # Create test data
        test_data = np.array([
            [2.5, -2.5, 0.0, 300.0, -300.0, 50.0],  # Values beyond normal ranges
            [1.0, -1.0, 1.0, 100.0, -100.0, 0.0]    # Values within normal ranges
        ])
        
        normalized = self.preprocessor.normalize_data(test_data)
        
        # Check that values are clipped and normalized
        # Acceleration should be clipped to [-2, 2] and normalized to [-1, 1]
        self.assertTrue(np.all(normalized[:, :3] >= -1.0))
        self.assertTrue(np.all(normalized[:, :3] <= 1.0))
        
        # Gyroscope should be clipped to [-250, 250] and normalized to [-1, 1]
        self.assertTrue(np.all(normalized[:, 3:] >= -1.0))
        self.assertTrue(np.all(normalized[:, 3:] <= 1.0))
    
    def test_extract_features(self):
        """Test feature extraction"""
        # Create test data
        test_data = np.random.rand(self.config.WINDOW_SIZE, self.config.FEATURES)
        
        features = self.preprocessor.extract_features(test_data)
        
        # Check output shape
        expected_shape = (1, self.config.WINDOW_SIZE, self.config.FEATURES)
        self.assertEqual(features.shape, expected_shape)

if __name__ == '__main__':
    unittest.main()