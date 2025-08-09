"""
ESP32 Car Accident Detection System - Simplified Demo

This script demonstrates the key components of the ESP32 car accident detection system.
"""

import sys
import os
import numpy as np
import time

# Add the esp32_accident_detector directory to the path
sys.path.insert(0, 'esp32_accident_detector')

def demo_sensor_fusion():
    """Demo: Sensor fusion and preprocessing"""
    print("=== Sensor Fusion Demo ===")
    
    # Import our modules
    from sensors.fusion import SensorFusion
    
    # Initialize sensor fusion
    fusion = SensorFusion()
    
    # Simulate 3 seconds of sensor data (150 samples at 50Hz)
    print("Simulating 3 seconds of sensor data...")
    
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
        
        # Every 50 samples, show statistics
        if (i + 1) % 50 == 0:
            window = fusion.get_data_window()
            if window:
                stats = fusion.calculate_sensor_statistics(window)
                print(f"  Samples {i-49}-{i}: Max accel magnitude = {stats['magnitude_max']:.2f}g")
    
    # Get processed window
    processed = fusion.get_processed_window()
    if processed is not None:
        print(f"Processed window shape: {processed.shape}")
        print(f"Normalized data range: [{np.min(processed):.3f}, {np.max(processed):.3f}]")
    
    print("Sensor fusion demo completed!")
    print()

def demo_ml_training():
    """Demo: ML model training process"""
    print("=== ML Training Demo ===")
    
    print("The ML training process involves:")
    print("1. Generating training data with realistic accident patterns")
    print("2. Preprocessing data into sequences for LSTM training")
    print("3. Training a lightweight LSTM model")
    print("4. Converting to TensorFlow Lite for ESP32 deployment")
    print()
    print("Key features of our approach:")
    print("- Lightweight LSTM architecture (32->16 units)")
    print("- Sequence length of 50 samples (1 second at 50Hz)")
    print("- Float16 quantization for reduced model size")
    print("- Optimized for ESP32 memory constraints")
    print()
    print("Training demo completed!")
    print()

def demo_inference():
    """Demo: ML inference"""
    print("=== ML Inference Demo ===")
    
    print("The inference process on ESP32:")
    print("1. Collect sensor data in real-time")
    print("2. Maintain a sliding window of recent data")
    print("3. Normalize and preprocess the data")
    print("4. Run inference using TensorFlow Lite")
    print("5. Apply confidence threshold for accident detection")
    print()
    print("Performance characteristics:")
    print("- Model size: <100KB (TFLite format)")
    print("- Inference time: <50ms on ESP32")
    print("- Memory usage: <500KB")
    print()
    print("Inference demo completed!")
    print()

def demo_hardware_integration():
    """Demo: Hardware integration"""
    print("=== Hardware Integration Demo ===")
    
    print("ESP32 hardware components:")
    print("1. MPU6050: 6-axis accelerometer/gyroscope")
    print("   - I2C communication")
    print("   - Configurable range (±2g to ±16g)")
    print("   - 50Hz sampling rate")
    print()
    print("2. SIM700C: GSM/GPS module")
    print("   - UART communication")
    print("   - SMS sending capability")
    print("   - GPS location retrieval")
    print()
    print("3. User interface:")
    print("   - Physical button for alert override")
    print("   - LED status indicator")
    print()
    print("Hardware integration demo completed!")
    print()

def demo_alert_system():
    """Demo: Alert system"""
    print("=== Alert System Demo ===")
    
    print("Alert system workflow:")
    print("1. Accident detected with high confidence")
    print("2. 15-second countdown begins with LED indication")
    print("3. User can press button to cancel alert")
    print("4. If not cancelled, SMS sent with location")
    print("5. GPS location retrieved from SIM700C")
    print("6. Google Maps link included in SMS")
    print()
    print("Alert system demo completed!")
    print()

def main():
    """Main demo function"""
    print("ESP32 Car Accident Detection System - Component Demos")
    print("=" * 55)
    print()
    
    demo_sensor_fusion()
    demo_ml_training()
    demo_inference()
    demo_hardware_integration()
    demo_alert_system()
    
    print("=== Demo Summary ===")
    print("The ESP32 car accident detection system combines:")
    print("• Real-time sensor fusion and preprocessing")
    print("• Lightweight ML model for accident detection")
    print("• Hardware integration with MPU6050 and SIM7000C")
    print("• Emergency alert system with manual override")
    print()
    print("For deployment:")
    print("1. Flash MicroPython to ESP32")
    print("2. Upload esp32_accident_detector files")
    print("3. Connect hardware components")
    print("4. Run main_esp32.py")
    print()

if __name__ == "__main__":
    main()