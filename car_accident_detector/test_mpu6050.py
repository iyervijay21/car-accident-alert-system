#!/usr/bin/env python3
"""
Test script for MPU6050 sensor
"""

import time
from sensors.mpu6050 import MPU6050

def main():
    print("Testing MPU6050 sensor...")
    
    try:
        # Initialize sensor
        sensor = MPU6050()
        print("MPU6050 initialized successfully")
        
        # Test reading data
        print("\nReading sensor data (press Ctrl+C to stop):")
        print("Accel X\t\tAccel Y\t\tAccel Z\t\tGyro X\t\tGyro Y\t\tGyro Z")
        print("-" * 80)
        
        for i in range(20):  # Read 20 samples
            data = sensor.read_sensor_data()
            print(f"{data[0]:.3f}g\t\t{data[1]:.3f}g\t\t{data[2]:.3f}g\t\t"
                  f"{data[3]:.1f}°/s\t\t{data[4]:.1f}°/s\t\t{data[5]:.1f}°/s")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()