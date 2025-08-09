import time
import threading
import RPi.GPIO as GPIO
from typing import Optional
import numpy as np

from .config import Config
from .sensors.mpu6050 import MPU6050
from .sensors.gps import GPSInterface
from .ml.preprocessing import DataPreprocessor
from .ml.inference import AccidentDetector
from .alert.sim7000c import SIM7000C

class CarAccidentDetector:
    \"\"\"
    Main controller for car accident detection system
    \"\"\"
    
    def __init__(self):
        self.config = Config()
        self.setup_gpio()
        
        # Initialize components
        self.mpu6050 = MPU6050()
        self.gps = GPSInterface()
        self.preprocessor = DataPreprocessor()
        self.detector = AccidentDetector()
        self.sim7000c = SIM7000C()
        
        # State variables
        self.accident_detected = False
        self.alert_timer = None
        self.system_active = True
        
        # Calibrate sensors
        self.calibrate_sensors()
        
    def setup_gpio(self):
        \"\"\"Setup GPIO pins\"\"\"
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.config.LED_PIN, GPIO.OUT)
        GPIO.output(self.config.LED_PIN, GPIO.LOW)
        
        # Add button interrupt
        GPIO.add_event_detect(
            self.config.BUTTON_PIN, 
            GPIO.FALLING, 
            callback=self.button_pressed, 
            bouncetime=300
        )
    
    def calibrate_sensors(self):
        \"\"\"Calibrate MPU6050 sensor\"\"\"
        print(\"Calibrating sensors...\")
        try:
            accel_offsets, gyro_offsets = self.mpu6050.calibrate()
            print(\"Sensor calibration completed\")
        except Exception as e:
            print(f\"Sensor calibration failed: {e}\")
    
    def initialize_communications(self):
        \"\"\"Initialize GPS and SIM7000C modules\"\"\"
        print(\"Initializing communications...\")
        
        # Initialize GPS
        if self.gps.connect():
            print(\"GPS module connected\")
        else:
            print(\"Failed to connect to GPS module\")
        
        # Initialize SIM7000C
        if self.sim7000c.connect() and self.sim7000c.initialize_module():
            print(\"SIM7000C module initialized\")
            # Check signal strength
            signal = self.sim7000c.get_signal_strength()
            if signal:
                print(f\"GSM signal strength: {signal} dBm\")
        else:
            print(\"Failed to initialize SIM7000C module\")
    
    def button_pressed(self, channel):
        \"\"\"Handle button press event\"\"\"
        print(\"Button pressed!\")
        if self.accident_detected:
            self.cancel_alert()
    
    def start_alert_timer(self):
        \"\"\"Start timer for sending alert\"\"\"
        if self.alert_timer is None:
            print(f\"Accident detected! Sending alert in {self.config.ALERT_DELAY} seconds...\")
            print(\"Press button to cancel...\")
            GPIO.output(self.config.LED_PIN, GPIO.HIGH)
            self.alert_timer = threading.Timer(
                self.config.ALERT_DELAY, 
                self.send_alert
            )
            self.alert_timer.start()
    
    def cancel_alert(self):
        \"\"\"Cancel pending alert\"\"\"
        if self.alert_timer and self.alert_timer.is_alive():
            self.alert_timer.cancel()
            self.alert_timer = None
            self.accident_detected = False
            GPIO.output(self.config.LED_PIN, GPIO.LOW)
            print(\"Alert cancelled!\")
    
    def send_alert(self):
        \"\"\"Send accident alert\"\"\"
        print(\"Sending emergency alert...\")
        
        # Get current location
        location_link = self.gps.get_google_maps_link()
        if not location_link:
            print(\"Warning: No GPS location available\")
        
        # Send SMS alert
        success = self.sim7000c.send_alert(self.config.PHONE_NUMBER, location_link)
        
        if success:
            print(\"Emergency alert sent successfully!\")
        else:
            print(\"Failed to send emergency alert!\")
        
        # Reset state
        self.alert_timer = None
        GPIO.output(self.config.LED_PIN, GPIO.LOW)
    
    def run_detection_loop(self):
        \"\"\"Main detection loop\"\"\"
        print(\"Starting accident detection...\")
        print(\"Press Ctrl+C to stop\")
        
        try:
            while self.system_active:
                # Read sensor data
                sensor_data = self.mpu6050.read_sensor_data()
                
                # Add to preprocessor buffer
                self.preprocessor.add_data(sensor_data)
                
                # Get processed data window
                processed_data = self.preprocessor.get_processed_window()
                
                # Run inference if we have enough data
                if processed_data is not None:
                    is_accident, confidence = self.detector.predict(processed_data)
                    
                    if is_accident and not self.accident_detected:
                        print(f\"Accident detected! Confidence: {confidence:.3f}\")
                        self.accident_detected = True
                        self.start_alert_timer()
                
                # Small delay to control sampling rate
                time.sleep(1.0 / self.config.SAMPLING_RATE)
                
        except KeyboardInterrupt:
            print(\"\
Stopping detection system...\")
            self.system_active = False
    
    def run(self):
        \"\"\"Main application entry point\"\"\"
        try:
            # Initialize communications
            self.initialize_communications()
            
            # Start detection loop
            self.run_detection_loop()
            
        except Exception as e:
            print(f\"Error in main application: {e}\")
        finally:
            # Cleanup
            GPIO.cleanup()
            print(\"System shutdown complete\")

if __name__ == \"__main__\":
    detector = CarAccidentDetector()
    detector.run()