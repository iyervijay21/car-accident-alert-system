import numpy as np
from typing import List, Tuple, Optional
import time
from config import Config

class SensorFusion:
    """
    Efficient sensor fusion and preprocessing for accelerometer, gyroscope, and GPS data
    optimized for ESP32 embedded use.
    """
    
    def __init__(self):
        self.config = Config()
        self.window_size = self.config.WINDOW_SIZE
        self.features = self.config.FEATURES
        self.data_buffer = []
        self.gps_buffer = []
        
        # Pre-allocate arrays for efficiency
        self.accel_range = float(self.config.ACCELEROMETER_RANGE)
        self.gyro_range = float(self.config.GYROSCOPE_RANGE)
        
        # Normalization factors
        self.accel_norm_factor = 1.0 / self.accel_range
        self.gyro_norm_factor = 1.0 / self.gyro_range
        
    def add_sensor_data(self, accel_data: Tuple[float, float, float], 
                       gyro_data: Tuple[float, float, float],
                       timestamp: Optional[float] = None):
        """
        Add new sensor data to buffer
        accel_data: (accel_x, accel_y, accel_z) in g
        gyro_data: (gyro_x, gyro_y, gyro_z) in deg/s
        timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
            
        sensor_entry = {
            'timestamp': timestamp,
            'accel_x': accel_data[0],
            'accel_y': accel_data[1],
            'accel_z': accel_data[2],
            'gyro_x': gyro_data[0],
            'gyro_y': gyro_data[1],
            'gyro_z': gyro_data[2]
        }
        
        self.data_buffer.append(sensor_entry)
        
        # Keep only the last window_size samples for memory efficiency
        if len(self.data_buffer) > self.window_size:
            self.data_buffer.pop(0)
    
    def add_gps_data(self, latitude: float, longitude: float, 
                     timestamp: Optional[float] = None):
        """
        Add GPS data to buffer
        """
        if timestamp is None:
            timestamp = time.time()
            
        gps_entry = {
            'timestamp': timestamp,
            'latitude': latitude,
            'longitude': longitude
        }
        
        self.gps_buffer.append(gps_entry)
        
        # Keep only recent GPS data (last 5 minutes)
        cutoff_time = time.time() - 300  # 5 minutes
        self.gps_buffer = [entry for entry in self.gps_buffer 
                          if entry['timestamp'] > cutoff_time]
    
    def get_recent_gps(self) -> Optional[Tuple[float, float, float]]:
        """
        Get most recent GPS data
        Returns: (latitude, longitude, timestamp) or None if unavailable
        """
        if not self.gps_buffer:
            return None
            
        latest = self.gps_buffer[-1]
        return (latest['latitude'], latest['longitude'], latest['timestamp'])
    
    def get_data_window(self) -> Optional[List[dict]]:
        """
        Get current data window
        Returns: List of sensor data entries or None if insufficient data
        """
        if len(self.data_buffer) < self.window_size:
            return None
        return self.data_buffer[-self.window_size:]
    
    def normalize_sensor_data(self, data_window: List[dict]) -> np.ndarray:
        """
        Normalize sensor data for ML model input
        Optimized for embedded systems with pre-calculated factors
        """
        # Convert to numpy array for efficient processing
        accel_x = np.array([entry['accel_x'] for entry in data_window])
        accel_y = np.array([entry['accel_y'] for entry in data_window])
        accel_z = np.array([entry['accel_z'] for entry in data_window])
        gyro_x = np.array([entry['gyro_x'] for entry in data_window])
        gyro_y = np.array([entry['gyro_y'] for entry in data_window])
        gyro_z = np.array([entry['gyro_z'] for entry in data_window])
        
        # Clip and normalize acceleration data
        accel_x = np.clip(accel_x, -self.accel_range, self.accel_range) * self.accel_norm_factor
        accel_y = np.clip(accel_y, -self.accel_range, self.accel_range) * self.accel_norm_factor
        accel_z = np.clip(accel_z, -self.accel_range, self.accel_range) * self.accel_norm_factor
        
        # Clip and normalize gyroscope data
        gyro_x = np.clip(gyro_x, -self.gyro_range, self.gyro_range) * self.gyro_norm_factor
        gyro_y = np.clip(gyro_y, -self.gyro_range, self.gyro_range) * self.gyro_norm_factor
        gyro_z = np.clip(gyro_z, -self.gyro_range, self.gyro_range) * self.gyro_norm_factor
        
        # Stack into final array (samples, features)
        normalized_data = np.stack([accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z], axis=1)
        
        return normalized_data
    
    def extract_features(self, data_window: List[dict]) -> Optional[np.ndarray]:
        """
        Extract features from sensor data window
        Returns: Normalized numpy array of shape (1, window_size, features) or None
        """
        if data_window is None or len(data_window) == 0:
            return None
            
        # Normalize the data
        normalized_data = self.normalize_sensor_data(data_window)
        
        # Reshape for LSTM model input (batch_size, timesteps, features)
        return normalized_data.reshape(1, self.window_size, self.features)
    
    def get_processed_window(self) -> Optional[np.ndarray]:
        """
        Get fully processed data window ready for model inference
        """
        window = self.get_data_window()
        if window is None:
            return None
        return self.extract_features(window)
    
    def calculate_sensor_statistics(self, data_window: List[dict]) -> dict:
        """
        Calculate statistical features from sensor data for additional context
        """
        if data_window is None or len(data_window) == 0:
            return {}
        
        # Extract data arrays
        accel_data = np.array([[entry['accel_x'], entry['accel_y'], entry['accel_z']] 
                              for entry in data_window])
        gyro_data = np.array([[entry['gyro_x'], entry['gyro_y'], entry['gyro_z']] 
                             for entry in data_window])
        
        # Calculate statistics
        stats = {
            'accel_mean': np.mean(accel_data, axis=0).tolist(),
            'accel_std': np.std(accel_data, axis=0).tolist(),
            'accel_max': np.max(accel_data, axis=0).tolist(),
            'gyro_mean': np.mean(gyro_data, axis=0).tolist(),
            'gyro_std': np.std(gyro_data, axis=0).tolist(),
            'gyro_max': np.max(gyro_data, axis=0).tolist(),
            'magnitude_max': float(np.max(np.linalg.norm(accel_data, axis=1)))
        }
        
        return stats