"""
ESP32 Car Accident Detection System - Inference Test

This script demonstrates how to use the trained model for inference.
"""

import sys
import os
import numpy as np

# Add the esp32_accident_detector directory to the path
sys.path.insert(0, 'esp32_accident_detector')

def test_inference():
    """Test the inference with the trained model"""
    print("Testing ML Inference with Trained Model")
    print("=" * 40)
    
    # Import our inference module
    from ml.inference import AccidentDetector
    
    # Initialize the detector with our trained model
    model_path = 'esp32_accident_detector/accident_model.tflite'
    detector = AccidentDetector(model_path)
    
    # Print model info
    info = detector.get_model_info()
    print(f"Model info: {info}")
    
    if not info.get("loaded", False):
        print("Failed to load model. Exiting.")
        return
    
    # Generate some test data (normal driving)
    print("\nTesting with normal driving data...")
    normal_data = np.random.normal(0, 0.5, (1, 50, 6))
    # Scale to match our training data ranges
    normal_data[:, :, :3] = np.clip(normal_data[:, :, :3], -2.0, 2.0) / 2.0  # Acceleration
    normal_data[:, :, 3:] = np.clip(normal_data[:, :, 3:], -250.0, 250.0) / 250.0  # Gyroscope
    
    is_accident, confidence = detector.predict(normal_data)
    print(f"Normal driving - Accident: {is_accident}, Confidence: {confidence:.4f}")
    
    # Generate some test data (accident simulation)
    print("\nTesting with accident simulation data...")
    accident_data = np.random.normal(0, 3.0, (1, 50, 6))
    # Scale to match our training data ranges
    accident_data[:, :, :3] = np.clip(accident_data[:, :, :3], -2.0, 2.0) / 2.0  # Acceleration
    accident_data[:, :, 3:] = np.clip(accident_data[:, :, 3:], -250.0, 250.0) / 250.0  # Gyroscope
    
    is_accident, confidence = detector.predict(accident_data)
    print(f"Accident simulation - Accident: {is_accident}, Confidence: {confidence:.4f}")
    
    print("\nInference test completed!")

if __name__ == "__main__":
    test_inference()