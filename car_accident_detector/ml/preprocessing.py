import numpy as np
from typing import List, Tuple
from ..config import Config

class DataPreprocessor:
    """
    Preprocess sensor data for ML model input
    """
    
    def __init__(self):
        self.config = Config()
        self.window_size = self.config.WINDOW_SIZE
        self.features = self.config.FEATURES
        self.data_buffer = []
        
    def add_data(self, sensor_data: Tuple[float, float, float, float, float, float]):
        """
        Add new sensor data to buffer
        sensor_data: (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
        """
        self.data_buffer.append(sensor_data)
        # Keep only the last window_size samples
        if len(self.data_buffer) > self.window_size:
            self.data_buffer.pop(0)
    
    def get_window(self) -> np.ndarray:
        """
        Get current data window as numpy array
        Returns: numpy array of shape (window_size, features)
        """
        if len(self.data_buffer) < self.window_size:
            return None
            
        # Convert to numpy array
        data_array = np.array(self.data_buffer[-self.window_size:])
        return data_array
    
    def normalize_data(self, data: np.ndarray) -> np.ndarray:
        """
        Normalize sensor data
        """
        # Normalize acceleration data (typically -2g to +2g)
        data[:, :3] = np.clip(data[:, :3], -2.0, 2.0) / 2.0
        
        # Normalize gyroscope data (typically -250 to +250 deg/s)
        data[:, 3:] = np.clip(data[:, 3:], -250.0, 250.0) / 250.0
        
        return data
    
    def extract_features(self, data: np.ndarray) -> np.ndarray:
        """
        Extract statistical features from sensor data
        """
        if data is None or len(data) == 0:
            return None
            
        # Normalize the data first
        normalized_data = self.normalize_data(data)
        
        # For real-time inference, we'll use the raw normalized data
        # In a more advanced setup, we could extract features like:
        # - Mean, std, min, max for each axis
        # - FFT features
        # - Energy features
        
        # Reshape for model input (batch_size, timesteps, features)
        return normalized_data.reshape(1, self.window_size, self.features)
    
    def get_processed_window(self) -> np.ndarray:
        """
        Get fully processed data window ready for model inference
        """
        window = self.get_window()
        if window is None:
            return None
        return self.extract_features(window)