"""
ESP32 Car Accident Detection System - MicroPython Implementation

This is the main application file for running on an actual ESP32 board
using MicroPython. It demonstrates the hardware-specific implementation
that would be used in the real embedded system.

To run on ESP32:
1. Install MicroPython on your ESP32 board
2. Upload all files in the esp32_accident_detector directory
3. Run this file using:
   import main_esp32
   main_esp32.run()
"""

import time
import machine
from machine import Pin, I2C, UART, Timer
import ujson
import gc

# Import our modules
try:
    from config import Config
    from sensors.mpu6050_esp32 import MPU6050_ESP32
    from sensors.fusion import SensorFusion
    from ml.inference import AccidentDetector
    # Note: SIM7000C implementation would need to be adapted for MicroPython
    # from alert.sim7000c_esp32 import SIM7000C_ESP32
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all modules are uploaded to the ESP32")

class ESP32CarAccidentDetector:
    """
    ESP32-specific implementation of the car accident detection system
    """
    
    def __init__(self):
        self.config = Config()
        self.setup_hardware()
        
        # Initialize components
        self.setup_sensors()
        self.setup_ml()
        self.setup_alerts()
        
        # State variables
        self.accident_detected = False
        self.alert_timer = None
        self.system_active = True
        self.last_gps_update = 0
        
        print("ESP32 Car Accident Detector initialized")
    
    def setup_hardware(self):
        """Setup ESP32 hardware pins"""
        # Setup button with interrupt
        self.button = Pin(self.config.BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)
        
        # Setup LED
        self.led = Pin(self.config.LED_PIN, Pin.OUT)
        self.led.off()
        
        # Setup I2C for MPU6050
        self.i2c = I2C(0, scl=Pin(self.config.MPU6050_SCL_PIN), 
                       sda=Pin(self.config.MPU6050_SDA_PIN), freq=400000)
        
        # Setup UART for SIM7000C
        self.uart = UART(1, baudrate=self.config.BAUD_RATE, 
                         tx=Pin(self.config.SIM7000C_TX_PIN), 
                         rx=Pin(self.config.SIM7050_RX_PIN))
    
    def setup_sensors(self):
        """Setup sensors"""
        try:
            self.mpu6050 = MPU6050_ESP32(self.i2c, 
                                        accel_range=self.config.ACCELEROMETER_RANGE,
                                        gyro_range=self.config.GYROSCOPE_RANGE)
            print("MPU6050 initialized")
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
            self.mpu6050 = None
        
        self.sensor_fusion = SensorFusion()
    
    def setup_ml(self):
        """Setup ML inference"""
        try:
            self.detector = AccidentDetector()
            if not self.detector.model_loaded:
                print("Warning: ML model not loaded")
        except Exception as e:
            print(f"Failed to initialize ML detector: {e}")
            self.detector = None
    
    def setup_alerts(self):
        """Setup alert system"""
        # SIM7000C setup would go here
        # self.sim7000c = SIM7000C_ESP32(self.uart)
        print("Alert system initialized (mock)")
    
    def button_pressed(self, pin):
        """Handle button press interrupt"""
        # Debounce
        time.sleep_ms(50)
        if self.button.value() == 0:  # Still pressed
            print("Button pressed!")
            if self.accident_detected:
                self.cancel_alert()
    
    def read_sensors(self):
        """Read sensor data"""
        if self.mpu6050 is None:
            # Fallback to simulated data for testing
            import urandom
            accel = (urandom.random() - 0.5, urandom.random() - 0.5, 1.0)
            gyro = (urandom.random() - 0.5, urandom.random() - 0.5, urandom.random() - 0.5)
            return accel, gyro
        
        try:
            accel = self.mpu6050.get_acceleration()
            gyro = self.mpu6050.get_gyroscope()
            return accel, gyro
        except Exception as e:
            print(f"Sensor read error: {e}")
            return (0, 0, 0), (0, 0, 0)
    
    def start_alert_timer(self):
        """Start alert timer"""
        if self.alert_timer is None:
            print(f"Accident detected! Alert in {self.config.ALERT_DELAY} seconds...")
            self.led.on()
            
            # Use ESP32 timer
            self.alert_timer = Timer(-1)  # Virtual timer
            self.alert_timer.init(period=self.config.ALERT_DELAY * 1000, 
                                 mode=Timer.ONE_SHOT, callback=self.send_alert)
    
    def cancel_alert(self):
        """Cancel pending alert"""
        if self.alert_timer is not None:
            self.alert_timer.deinit()
            self.alert_timer = None
            self.accident_detected = False
            self.led.off()
            print("Alert cancelled!")
    
    def send_alert(self, timer=None):
        """Send accident alert (timer callback)"""
        print("Sending emergency alert...")
        
        # In a real implementation, this would send an SMS
        # For now, we just print a message
        print("EMERGENCY: Car accident detected!")
        print("Location: Unknown (GPS not implemented in this example)")
        
        # Reset
        self.alert_timer = None
        self.led.off()
    
    def run_detection_loop(self):
        """Main detection loop"""
        print("Starting detection loop...")
        print("Press button to stop")
        
        sample_period_ms = int(1000 / self.config.SAMPLING_RATE)
        last_sample = time.ticks_ms()
        
        while self.system_active:
            # Check if it's time for next sample
            now = time.ticks_ms()
            if time.ticks_diff(now, last_sample) >= sample_period_ms:
                last_sample = now
                
                # Read sensors
                accel_data, gyro_data = self.read_sensors()
                
                # Add to fusion buffer
                self.sensor_fusion.add_sensor_data(accel_data, gyro_data)
                
                # Get processed data
                processed_data = self.sensor_fusion.get_processed_window()
                
                # Run inference
                if processed_data is not None and self.detector is not None:
                    is_accident, confidence = self.detector.predict(processed_data)
                    
                    if is_accident and not self.accident_detected:
                        print(f"Accident detected! Confidence: {confidence:.3f}")
                        self.accident_detected = True
                        self.start_alert_timer()
                
                # Periodic cleanup
                if time.ticks_diff(now, last_sample) % 5000 < sample_period_ms:  # Every 5 seconds
                    gc.collect()  # Run garbage collection
    
    def stop(self):
        """Stop the system"""
        self.system_active = False
        if self.alert_timer is not None:
            self.alert_timer.deinit()
        self.led.off()
        print("System stopped")

# Global instance
detector = None

def run():
    """Main entry point"""
    global detector
    
    try:
        detector = ESP32CarAccidentDetector()
        detector.run_detection_loop()
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if detector is not None:
            detector.stop()
        print("System shutdown complete")

def stop():
    """Stop the running system"""
    global detector
    if detector is not None:
        detector.stop()

# For direct execution
if __name__ == "__main__":
    run()