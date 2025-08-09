import time
from typing import Tuple

class MPU6050_ESP32:
    """
    ESP32-specific implementation of MPU6050 interface
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
    
    def __init__(self, i2c_bus, accel_range: int = 2, gyro_range: int = 250):
        """
        Initialize MPU6050 sensor
        i2c_bus: Initialized I2C bus object
        accel_range: Accelerometer range (2, 4, 8, or 16 g)
        gyro_range: Gyroscope range (250, 500, 1000, or 2000 deg/s)
        """
        self.i2c = i2c_bus
        self.accel_range = accel_range
        self.gyro_range = gyro_range
        self._initialize()
    
    def _initialize(self):
        """Initialize the MPU6050 sensor"""
        # Wake up the MPU6050
        self.i2c.writeto_mem(self.MPU6050_ADDR, self.PWR_MGMT_1, b'\x00')
        time.sleep_ms(100)
        
        # Configure accelerometer range
        accel_range_reg = {
            2: 0x00,   # ±2g
            4: 0x08,   # ±4g
            8: 0x10,   # ±8g
            16: 0x18   # ±16g
        }.get(self.accel_range, 0x00)
        
        self.i2c.writeto_mem(self.MPU6050_ADDR, self.ACCEL_CONFIG, 
                            bytes([accel_range_reg]))
        
        # Configure gyroscope range
        gyro_range_reg = {
            250: 0x00,   # ±250°/s
            500: 0x08,   # ±500°/s
            1000: 0x10,  # ±1000°/s
            2000: 0x18   # ±2000°/s
        }.get(self.gyro_range, 0x00)
        
        self.i2c.writeto_mem(self.MPU6050_ADDR, self.GYRO_CONFIG, 
                            bytes([gyro_range_reg]))
    
    def _read_word(self, reg: int) -> int:
        """Read a 16-bit word from the sensor"""
        data = self.i2c.readfrom_mem(self.MPU6050_ADDR, reg, 2)
        value = (data[0] << 8) | data[1]
        # Convert to signed 16-bit integer
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value
    
    def get_acceleration(self) -> Tuple[float, float, float]:
        """
        Read acceleration data in g
        Returns: (accel_x, accel_y, accel_z) in g
        """
        accel_x = self._read_word(self.ACCEL_XOUT_H)
        accel_y = self._read_word(self.ACCEL_YOUT_H)
        accel_z = self._read_word(self.ACCEL_ZOUT_H)
        
        # Convert to g based on range
        accel_divisor = {
            2: 16384.0,
            4: 8192.0,
            8: 4096.0,
            16: 2048.0
        }[self.accel_range]
        
        return (
            accel_x / accel_divisor,
            accel_y / accel_divisor,
            accel_z / accel_divisor
        )
    
    def get_gyroscope(self) -> Tuple[float, float, float]:
        """
        Read gyroscope data in °/s
        Returns: (gyro_x, gyro_y, gyro_z) in °/s
        """
        gyro_x = self._read_word(self.GYRO_XOUT_H)
        gyro_y = self._read_word(self.GYRO_YOUT_H)
        gyro_z = self._read_word(self.GYRO_ZOUT_H)
        
        # Convert to °/s based on range
        gyro_divisor = {
            250: 131.0,
            500: 65.5,
            1000: 32.8,
            2000: 16.4
        }[self.gyro_range]
        
        return (
            gyro_x / gyro_divisor,
            gyro_y / gyro_divisor,
            gyro_z / gyro_divisor
        )
    
    def get_sensor_data(self) -> Tuple[float, float, float, float, float, float]:
        """
        Read all sensor data
        Returns: (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
        """
        accel = self.get_acceleration()
        gyro = self.get_gyroscope()
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
            accel = self.get_acceleration()
            gyro = self.get_gyroscope()
            
            for i in range(3):
                accel_sum[i] += accel[i]
                gyro_sum[i] += gyro[i]
            
            time.sleep_ms(10)
        
        accel_offsets = tuple(accel_sum[i] / samples for i in range(3))
        gyro_offsets = tuple(gyro_sum[i] / samples for i in range(3))
        
        # Gravity should be 1g on Z-axis when sensor is flat
        accel_offsets = (accel_offsets[0], accel_offsets[1], accel_offsets[2] - 1.0)
        
        print(f"Calibration complete. Accel offsets: {accel_offsets}, Gyro offsets: {gyro_offsets}")
        return accel_offsets, gyro_offsets

# Example usage for ESP32:
"""
from machine import I2C, Pin
import time

# Initialize I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Initialize MPU6050
mpu = MPU6050_ESP32(i2c)

# Read sensor data
while True:
    accel_data = mpu.get_acceleration()
    gyro_data = mpu.get_gyroscope()
    print(f"Accel: {accel_data}, Gyro: {gyro_data}")
    time.sleep(0.1)
"""