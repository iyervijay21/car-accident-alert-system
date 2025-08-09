#!/usr/bin/env python3
"""
Setup script for car accident detection system
"""

import os
import sys
import subprocess
from config import Config

def check_i2c_enabled():
    """Check if I2C interface is enabled"""
    try:
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        return 'i2c' in result.stdout
    except:
        return False

def enable_i2c():
    """Enable I2C interface (requires sudo)"""
    try:
        subprocess.run(['sudo', 'raspi-config', 'nonint', 'do_i2c', '0'], check=True)
        print("I2C interface enabled")
        return True
    except:
        print("Failed to enable I2C interface")
        return False

def install_dependencies():
    """Install Python dependencies"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("Python dependencies installed")
        return True
    except:
        print("Failed to install Python dependencies")
        return False

def create_directories():
    """Create necessary directories"""
    config = Config()
    
    directories = [
        config.DATA_DIR,
        "logs",
        "models"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    print("Setting up car accident detection system...")
    
    # Check if running on Raspberry Pi
    if not os.path.exists('/proc/device-tree/model'):
        print("Warning: Not running on a Raspberry Pi. Some features may not work.")
    
    # Enable I2C if needed
    if not check_i2c_enabled():
        print("I2C interface not enabled. Enabling now...")
        if not enable_i2c():
            print("Please enable I2C manually using 'sudo raspi-config'")
            return False
    
    # Install dependencies
    print("Installing Python dependencies...")
    if not install_dependencies():
        return False
    
    # Create directories
    print("Creating directories...")
    create_directories()
    
    # Generate sample training data
    print("Generating sample training data...")
    try:
        from generate_training_data import create_training_dataset
        import pandas as pd
        
        df = create_training_dataset(hours_normal=1, num_accidents=5)  # Small dataset for testing
        df.to_csv('sample_training_data.csv', index=False)
        print("Sample training data generated: sample_training_data.csv")
    except Exception as e:
        print(f"Failed to generate sample training data: {e}")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Connect hardware components according to README.md")
    print("2. Train the model: python3 ml/train_model.py --data sample_training_data.csv")
    print("3. Test individual components:")
    print("   - MPU6050: python3 test_mpu6050.py")
    print("   - GPS: python3 test_gps.py")
    print("   - SIM7000C: python3 test_sim7000c.py")
    print("4. Run the main system: python3 main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)