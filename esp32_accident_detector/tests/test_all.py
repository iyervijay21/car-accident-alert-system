import sys
import os
import numpy as np

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from sensors.fusion import SensorFusion
from ml.inference import AccidentDetector
from alert.sim7000c import MockSIM700C

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

def test_inference():
    """Test inference module"""
    print("Testing Inference module...")
    
    # Create a mock detector (will use fallback since we don't have a real model)
    detector = AccidentDetector()
    
    # Get model info
    info = detector.get_model_info()
    print(f"Model info: {info}")
    
    # Try prediction with dummy data
    dummy_data = np.random.rand(1, 50, 6).astype(np.float32)
    is_accident, confidence = detector.predict(dummy_data)
    print(f"Prediction result: is_accident={is_accident}, confidence={confidence:.3f}")
    print("Inference test completed")
    print()

def test_sim7000c():
    """Test SIM7000C module"""
    print("Testing SIM7000C module...")
    
    sim = MockSIM7000C()
    
    # Test initialization
    if sim.initialize_module():
        print("Module initialized successfully")
        
        # Test signal strength
        signal = sim.get_signal_strength()
        print(f"Signal strength: {signal} dBm")
        
        # Test GPS
        location = sim.get_gps_location()
        if location:
            lat, lon = location
            link = sim.get_google_maps_link(lat, lon)
            print(f"GPS location: {lat}, {lon}")
            print(f"Google Maps link: {link}")
        
        # Test SMS
        success = sim.send_sms("+1234567890", "Test message")
        print(f"SMS test: {'PASSED' if success else 'FAILED'}")
    else:
        print("Module initialization failed")
    
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
    test_inference()
    test_sim7000c()
    
    print("All tests completed!")

if __name__ == "__main__":
    main()