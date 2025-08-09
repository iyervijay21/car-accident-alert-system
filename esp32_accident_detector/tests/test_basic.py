import sys
import os
import numpy as np

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Mock serial for testing
class MockSerial:
    def __init__(self, *args, **kwargs):
        pass
    
    def write(self, data):
        pass
    
    def read(self, size):
        return b""
    
    def flushInput(self):
        pass
    
    def in_waiting(self):
        return 0

# Mock serial module
import sys
sys.modules['serial'] = MockSerial

from config import Config
from sensors.fusion import SensorFusion
# from ml.inference import AccidentDetector  # Requires TensorFlow
# from alert.sim7000c import MockSIM700C  # Requires serial

def test_sensor_fusion():
    """Test sensor fusion module"""
    print("Testing Sensor Fusion module...")
    
    fusion = SensorFusion()
    
    # Add some sample data
    for i in range(60):  # More than window size
        # Normal data
        accel = (0.1, 0.2, 9.8)  # Mostly gravity on Z-axis
        gyro = (0.5, 0.3, 0.1)
        fusion.add_sensor_data(accel, gyro, timestamp=i)
    
    # Get processed window
    processed = fusion.get_processed_window()
    if processed is not None:
        print(f"Processed window shape: {processed.shape}")
        print(f"Data range - Accel: [{np.min(processed[:,:,0]):.2f}, {np.max(processed[:,:,0]):.2f}]")
        print("Sensor Fusion test PASSED")
    else:
        print("Sensor Fusion test FAILED - insufficient data")
    
    print()

def test_config():
    """Test configuration"""
    print("Testing Configuration...")
    
    config = Config()
    print(f"Window size: {config.WINDOW_SIZE}")
    print(f"Sampling rate: {config.SAMPLING_RATE} Hz")
    print(f"Confidence threshold: {config.CONFIDENCE_THRESHOLD}")
    print(f"Alert delay: {config.ALERT_DELAY} seconds")
    print("Configuration test PASSED")
    print()

def main():
    """Run all tests"""
    print("ESP32 Car Accident Detector - Unit Tests")
    print("=" * 40)
    
    test_config()
    test_sensor_fusion()
    
    print("Basic tests completed!")

if __name__ == "__main__":
    main()