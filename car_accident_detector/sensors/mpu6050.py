import time
import math
from typing import Tuple, List
import smbus2
from ..config import Config

class MPU6050:
    """
    Interface for MPU6050 accelerometer and gyroscope sensor
    """
    
    # MPU6050 Registers
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    GYRO_XOUT_H = 0x43
    GYRO_YOUT_H = 0x45
    GYRO_ZOUT_H = 0x47
    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B
    
    def __init__(self, bus_number: int = 1):
        self.bus = smbus2.SMBus(bus_number)
        self.config = Config()
        self._initialize()
        
    def _initialize(self):
        """Initialize the MPU6050 sensor"""
        # Wake up the MPU6050
        self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0)
        
        # Configure accelerometer range
        accel_range = {
            2: 0x00,   # ±2g
            4: 0x08,   # ±4g
            8: 0x10,   # ±8g
            16: 0x18   # ±16g
        }[self.config.ACCELEROMETER_RANGE]
        self.bus.write_byte_data(self.MPU6050_ADDR, self.ACCEL_CONFIG, accel_range)
        
        # Configure gyroscope range
        gyro_range = {
            250: 0x00,   # ±250°/s
            500: 0x08,   # ±500°/s
            1000: 0x10,  # ±1000°/s
            2000: 0x18   # ±2000°/s
        }[self.config.GYROSCOPE_RANGE]
        self.bus.write_byte_data(self.MPU6050_ADDR, self.GYRO_CONFIG, gyro_range)
        
    def _read_word(self, reg: int) -> int:
        """Read a 16-bit word from the sensor"""
        high = self.bus.read_byte_data(self.MPU6050_ADDR, reg)
        low = self.bus.read_byte_data(self.MPU6050_ADDR, reg + 1)
        value = (high << 8) + low
        # Convert to signed 16-bit integer
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value
    
    def _read_acceleration(self) -> Tuple[float, float, float]:
        """Read acceleration data in g"""
        accel_x = self._read_word(self.ACCEL_XOUT_H)
        accel_y = self._read_word(self.ACCEL_YOUT_H)
        accel_z = self._read_word(self.ACCEL_ZOUT_H)
        
        # Convert to g based on range
        accel_divisor = {
            2: 16384.0,
            4: 8192.0,
            8: 4096.0,
            16: 2048.0
        }[self.config.ACCELEROMETER_RANGE]
        
        return (
            accel_x / accel_divisor,
            accel_y / accel_divisor,
            accel_z / accel_divisor
        )
    
    def _read_gyroscope(self) -> Tuple[float, float, float]:
        """Read gyroscope data in °/s"""
        gyro_x = self._read_word(self.GYRO_XOUT_H)
        gyro_y = self._read_word(self.GYRO_YOUT_H)
        gyro_z = self._read_word(self.GYRO_ZOUT_H)
        
        # Convert to °/s based on range
        gyro_divisor = {
            250: 131.0,
            500: 65.5,
            1000: 32.8,
            2000: 16.4
        }[self.config.GYROSCOPE_RANGE]
        
        return (
            gyro_x / gyro_divisor,
            gyro_y / gyro_divisor,
            gyro_z / gyro_divisor
        )
    
    def read_sensor_data(self) -> Tuple[float, float, float, float, float, float]:
        """
        Read all sensor data
        Returns: (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
        """
        accel = self._read_acceleration()
        gyro = self._read_gyroscope()
        return accel + gyro
    
    def calibrate(self, samples: int = 1000) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Calibrate the sensor by calculating offsets
        Returns: (accel_offsets, gyro_offsets)
        """
        accel_sum = [0.0, 0.0, 0.0]
        gyro_sum = [0.0, 0.0, 0.0]
        
        print("Calibrating MPU6050. Keep the sensor still...")
        for _ in range(samples):
            accel = self._read_acceleration()
            gyro = self._read_gyroscope()
            
            for i in range(3):
                accel_sum[i] += accel[i]
                gyro_sum[i] += gyro[i]
            
            time.sleep(0.01)
        
        accel_offsets = tuple(accel_sum[i] / samples for i in range(3))
        gyro_offsets = tuple(gyro_sum[i] / samples for i in range(3))
        
        # Gravity should be 1g on Z-axis when sensor is flat
        accel_offsets = (accel_offsets[0], accel_offsets[1], accel_offsets[2] - 1.0)
        
        print(f"Calibration complete. Accel offsets: {accel_offsets}, Gyro offsets: {gyro_offsets}")
        return accel_offsets, gyro_offsets