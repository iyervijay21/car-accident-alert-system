"""
ESP32 Car Accident Detection System - Complete Workflow Demo

This script demonstrates the complete workflow of the ESP32 car accident detection system:
1. Generate training data
2. Train ML model
3. Run inference on sample data
4. Simulate alert system

This is a simplified demonstration that runs on a PC for testing purposes.
"""

import numpy as np
import pandas as pd
import sys
import os
import time

# Add the esp32_accident_detector directory to the path
sys.path.insert(0, 'esp32_accident_detector')

# Import our modules
from config import Config
from sensors.fusion import SensorFusion
from ml.inference import AccidentDetector

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
sys.modules['serial'] = MockSerial

# Import the alert module (will use mock serial)
from alert.sim7000c import MockSIM700C

def demo_data_generation():
    """Demo: Generate training data"""
    print("=== Step 1: Generating Training Data ===")
    
    # Import the data generation script
    from esp32_accident_detector.ml.generate_data import generate_training_data
    
    # Generate a small dataset for demo
    df = generate_training_data(num_sequences=50, sequence_length=50)
    
    # Save to CSV
    df.to_csv('esp32_accident_detector/demo_training_data.csv', index=False)
    
    # Print statistics
    total_samples = len(df)
    accident_samples = df['label'].sum()
    normal_samples = total_samples - accident_samples
    
    print(f"Generated {total_samples} samples")
    print(f"Accident samples: {accident_samples} ({accident_samples/total_samples*100:.1f}%)")
    print(f"Normal samples: {normal_samples} ({normal_samples/total_samples*100:.1f}%)")
    print("Training data saved to demo_training_data.csv")
    print()
    
    return 'esp32_accident_detector/demo_training_data.csv'

def demo_model_training(data_file):
    """Demo: Train ML model"""
    print("=== Step 2: Training ML Model ===")
    
    # Import the training script
    from esp32_accident_detector.ml.train import train_model
    
    try:
        # Train a lightweight model
        model, history = train_model(
            data_file, 
            model_save_path='esp32_accident_detector/demo_model.h5',
            sequence_length=50,
            epochs=5
        )
        
        print("Model training completed!")
        print(f"Final validation accuracy: {max(history.history['val_accuracy']):.4f}")
        print("Model saved as demo_model.h5 and demo_model.tflite")
        print()
        
        return 'esp32_accident_detector/demo_model.h5'
        
    except Exception as e:
        print(f"Model training failed: {e}")
        print("Using fallback detector for demo")
        print()
        return None

def demo_inference(model_file):
    """Demo: Run inference"""
    print("=== Step 3: Running Inference ===")
    
    # Initialize sensor fusion
    fusion = SensorFusion()
    
    # Initialize detector (will use fallback if no model)
    detector = AccidentDetector(model_file)
    
    # Print model info
    info = detector.get_model_info()
    print(f"Model info: {info}")
    
    # Simulate sensor data for 3 seconds (150 samples at 50Hz)
    print("Simulating 3 seconds of sensor data...")
    
    accident_detected = False
    max_confidence = 0.0
    
    for i in range(150):
        # Generate sensor data
        # Most data is normal, but we'll inject an "accident" pattern
        if 75 <= i <= 100:  # Inject accident pattern in the middle
            # High acceleration/gyro values
            accel = (
                np.random.normal(0, 3.0),
                np.random.normal(0, 3.0),
                np.random.normal(0, 3.0)
            )
            gyro = (
                np.random.normal(0, 100.0),
                np.random.normal(0, 100.0),
                np.random.normal(0, 100.0)
            )
        else:
            # Normal driving data
            accel = (
                np.random.normal(0, 0.5),
                np.random.normal(0, 0.5),
                np.random.normal(1.0, 0.5)
            )
            gyro = (
                np.random.normal(0, 10.0),
                np.random.normal(0, 10.0),
                np.random.normal(0, 10.0)
            )
        
        # Add to fusion buffer
        fusion.add_sensor_data(accel, gyro, timestamp=time.time() + i * 0.02)
        
        # Get processed data
        processed_data = fusion.get_processed_window()
        
        # Run inference
        if processed_data is not None:
            is_accident, confidence = detector.predict(processed_data)
            max_confidence = max(max_confidence, confidence)
            
            if is_accident and not accident_detected:
                print(f"ACCIDENT DETECTED at sample {i} with confidence {confidence:.3f}!")
                accident_detected = True
    
    print(f"Maximum confidence during simulation: {max_confidence:.3f}")
    print("Inference demo completed!")
    print()

def demo_alert_system():
    """Demo: Alert system"""
    print("=== Step 4: Alert System Demo ===")
    
    # Initialize mock SIM7000C
    sim7000c = MockSIM7000C()
    
    # Initialize module
    if sim7000c.initialize_module():
        print("SIM7000C initialized successfully")
        
        # Get signal strength
        signal = sim7000c.get_signal_strength()
        print(f"Signal strength: {signal} dBm")
        
        # Get GPS location
        location = sim7000c.get_gps_location()
        if location:
            lat, lon = location
            link = sim7000c.get_google_maps_link(lat, lon)
            print(f"Current location: {lat}, {lon}")
            
            # Send alert
            success = sim7000c.send_alert("+1234567890", link)
            if success:
                print("Emergency alert sent successfully!")
            else:
                print("Failed to send emergency alert")
        else:
            print("No GPS location available")
    else:
        print("Failed to initialize SIM7000C")
    
    print("Alert system demo completed!")
    print()

def main():
    """Main demo function"""
    print("ESP32 Car Accident Detection System - Complete Workflow Demo")
    print("=" * 60)
    print()
    
    # Step 1: Generate training data
    data_file = demo_data_generation()
    
    # Step 2: Train model
    model_file = demo_model_training(data_file)
    
    # Step 3: Run inference
    demo_inference(model_file)
    
    # Step 4: Demo alert system
    demo_alert_system()
    
    print("=== Demo Completed ===")
    print("The ESP32 car accident detection system is ready for deployment!")
    print()
    print("For ESP32 deployment:")
    print("1. Flash MicroPython to your ESP32 board")
    print("2. Upload all files in the esp32_accident_detector directory")
    print("3. Run main_esp32.py on the ESP32")
    print("4. Connect MPU6050 and SIM7000C hardware")

if __name__ == "__main__":
    main()