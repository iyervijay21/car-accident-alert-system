import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Config:
    # Sensor configuration
    ACCELEROMETER_RANGE: int = 2  # ±2g range
    GYROSCOPE_RANGE: int = 250    # ±250°/s range
    SAMPLING_RATE: int = 50       # 50 Hz sampling rate
    
    # Data preprocessing
    WINDOW_SIZE: int = 50         # 1 second of data at 50Hz
    FEATURES: int = 6             # accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
    
    # Model configuration
    MODEL_PATH: str = "models/accident_model.tflite"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Alert configuration
    ALERT_DELAY: int = 15         # 15 seconds delay before sending alert
    PHONE_NUMBER: str = "+1234567890"  # Emergency contact
    GPS_POLL_INTERVAL: int = 10   # GPS update interval in seconds
    
    # Hardware pins (ESP32 specific)
    BUTTON_PIN: int = 18          # GPIO pin for override button
    LED_PIN: int = 2              # GPIO pin for status LED (built-in LED on most ESP32 boards)
    MPU6050_SDA_PIN: int = 21     # I2C SDA pin for MPU6050
    MPU6050_SCL_PIN: int = 22     # I2C SCL pin for MPU6050
    SIM7000C_RX_PIN: int = 16     # UART RX pin for SIM7000C
    SIM7000C_TX_PIN: int = 17     # UART TX pin for SIM7000C
    
    # Data storage
    DATA_DIR: str = "data"
    LOG_FILE: str = "logs/sensor_data.csv"
    
    # SIM7000C configuration
    SERIAL_PORT: str = "/dev/uart/1"  # ESP32 UART1
    BAUD_RATE: int = 115200
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables"""
        return cls(
            ACCELEROMETER_RANGE=int(os.getenv("ACCEL_RANGE", "2")),
            GYROSCOPE_RANGE=int(os.getenv("GYRO_RANGE", "250")),
            SAMPLING_RATE=int(os.getenv("SAMPLING_RATE", "50")),
            CONFIDENCE_THRESHOLD=float(os.getenv("CONFIDENCE_THRESHOLD", "0.7")),
            PHONE_NUMBER=os.getenv("PHONE_NUMBER", "+1234567890"),
        )