import time
import threading
from typing import Optional
import numpy as np

from config import Config
from sensors.fusion import SensorFusion
from ml.inference import AccidentDetector
from alert.sim7000c import SIM7000C, MockSIM700C

# For ESP32, we would use machine module instead of GPIO
# For PC testing, we'll create a mock GPIO interface
class MockGPIO:
    """Mock GPIO implementation for testing on PC"""
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    HIGH = 1
    LOW = 0
    
    pins = {}
    callbacks = {}
    
    @staticmethod
    def setmode(mode):
        print(f"Mock GPIO: Set mode to {mode}")
    
    @staticmethod
    def setup(pin, direction, pull_up_down=None):
        MockGPIO.pins[pin] = {"direction": direction, "value": 0}
        print(f"Mock GPIO: Setup pin {pin} as {direction}")
    
    @staticmethod
    def output(pin, value):
        if pin in MockGPIO.pins:
            MockGPIO.pins[pin]["value"] = value
            print(f"Mock GPIO: Set pin {pin} to {value}")
    
    @staticmethod
    def input(pin):
        return MockGPIO.pins.get(pin, {}).get("value", 0)
    
    @staticmethod
    def add_event_detect(pin, edge, callback, bouncetime=300):
        MockGPIO.callbacks[pin] = callback
        print(f"Mock GPIO: Added event detect on pin {pin}")
    
    @staticmethod
    def simulate_button_press(pin):
        """Simulate button press for testing"""
        if pin in MockGPIO.callbacks:
            MockGPIO.callbacks[pin](pin)

# For ESP32, you would import from machine:
# from machine import Pin, Timer
# For PC testing, we use our mock
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = MockGPIO

class ESP32CarAccidentDetector:
    """
    Main controller for ESP32 car accident detection system
    """
    
    def __init__(self, use_mock=False):
        self.config = Config()
        self.use_mock = use_mock
        self.setup_gpio()
        
        # Initialize components
        self.sensor_fusion = SensorFusion()
        self.detector = AccidentDetector()
        
        # Use mock or real SIM7000C
        if use_mock:
            self.sim7000c = MockSIM7000C()
        else:
            self.sim7000c = SIM7000C()
        
        # State variables
        self.accident_detected = False
        self.alert_timer = None
        self.system_active = True
        self.last_gps_update = 0
        
        # Initialize communications
        self.initialize_communications()
    
    def setup_gpio(self):
        """Setup GPIO pins"""
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
    
    def initialize_communications(self):
        """Initialize SIM7000C module"""
        print("Initializing communications...")
        
        # Initialize SIM7000C
        if self.sim7000c.connect() and self.sim7000c.initialize_module():
            print("SIM7000C module initialized")
            # Check signal strength
            signal = self.sim7000c.get_signal_strength()
            if signal:
                print(f"GSM signal strength: {signal} dBm")
        else:
            print("Failed to initialize SIM7000C module")
    
    def button_pressed(self, channel):
        """Handle button press event"""
        print("Button pressed!")
        if self.accident_detected:
            self.cancel_alert()
    
    def start_alert_timer(self):
        """Start timer for sending alert"""
        if self.alert_timer is None:
            print(f"Accident detected! Sending alert in {self.config.ALERT_DELAY} seconds...")
            print("Press button to cancel...")
            GPIO.output(self.config.LED_PIN, GPIO.HIGH)
            
            # For ESP32, you would use Timer:
            # self.alert_timer = Timer(-1)  # Virtual timer
            # self.alert_timer.init(period=self.config.ALERT_DELAY * 1000, 
            #                      mode=Timer.ONE_SHOT, callback=self.send_alert)
            
            # For PC testing, we use threading
            if not self.use_mock:
                self.alert_timer = threading.Timer(
                    self.config.ALERT_DELAY, 
                    self.send_alert
                )
                self.alert_timer.start()
            else:
                # In mock mode, send alert immediately for testing
                self.send_alert()
    
    def cancel_alert(self):
        """Cancel pending alert"""
        if self.alert_timer:
            if not self.use_mock:
                self.alert_timer.cancel()
            self.alert_timer = None
            self.accident_detected = False
            GPIO.output(self.config.LED_PIN, GPIO.LOW)
            print("Alert cancelled!")
    
    def send_alert(self):
        """Send accident alert"""
        print("Sending emergency alert...")
        
        # Get current location
        location = self.sim7000c.get_gps_location()
        location_link = None
        if location:
            lat, lon = location
            location_link = self.sim7000c.get_google_maps_link(lat, lon)
            print(f"Location: {lat}, {lon}")
        else:
            print("Warning: No GPS location available")
        
        # Send SMS alert
        success = self.sim7000c.send_alert(self.config.PHONE_NUMBER, location_link)
        
        if success:
            print("Emergency alert sent successfully!")
        else:
            print("Failed to send emergency alert!")
        
        # Reset state
        self.alert_timer = None
        GPIO.output(self.config.LED_PIN, GPIO.LOW)
    
    def simulate_sensor_data(self):
        """
        Simulate sensor data for testing
        In a real implementation, this would read from actual sensors
        """
        # Generate realistic sensor data
        # Normal driving data most of the time, with occasional spikes
        is_accident = np.random.random() < 0.01  # 1% chance of accident data
        
        if is_accident:
            # Accident data - high acceleration/gyro values
            accel_x = np.random.normal(0, 3.0)
            accel_y = np.random.normal(0, 3.0)
            accel_z = np.random.normal(0, 3.0)
            gyro_x = np.random.normal(0, 100.0)
            gyro_y = np.random.normal(0, 100.0)
            gyro_z = np.random.normal(0, 100.0)
        else:
            # Normal driving data
            accel_x = np.random.normal(0, 0.5)
            accel_y = np.random.normal(0, 0.5)
            accel_z = np.random.normal(1.0, 0.5)  # Gravity on Z-axis
            gyro_x = np.random.normal(0, 10.0)
            gyro_y = np.random.normal(0, 10.0)
            gyro_z = np.random.normal(0, 10.0)
        
        return (accel_x, accel_y, accel_z), (gyro_x, gyro_y, gyro_z)
    
    def update_gps(self):
        """
        Update GPS data periodically
        """
        current_time = time.time()
        if current_time - self.last_gps_update > self.config.GPS_POLL_INTERVAL:
            location = self.sim7000c.get_gps_location()
            if location:
                lat, lon = location
                self.sensor_fusion.add_gps_data(lat, lon, current_time)
                print(f"GPS updated: {lat}, {lon}")
            self.last_gps_update = current_time
    
    def run_detection_loop(self):
        """Main detection loop"""
        print("Starting accident detection...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.system_active:
                # Simulate reading sensor data
                # In real implementation, this would read from MPU6050
                accel_data, gyro_data = self.simulate_sensor_data()
                
                # Add to sensor fusion buffer
                self.sensor_fusion.add_sensor_data(accel_data, gyro_data)
                
                # Update GPS periodically
                self.update_gps()
                
                # Get processed data window
                processed_data = self.sensor_fusion.get_processed_window()
                
                # Run inference if we have enough data
                if processed_data is not None:
                    is_accident, confidence = self.detector.predict(processed_data)
                    
                    if is_accident and not self.accident_detected:
                        print(f"Accident detected! Confidence: {confidence:.3f}")
                        self.accident_detected = True
                        self.start_alert_timer()
                
                # Small delay to control sampling rate
                time.sleep(1.0 / self.config.SAMPLING_RATE)
                
        except KeyboardInterrupt:
            print("\nStopping detection system...")
            self.system_active = False
    
    def run(self):
        """Main application entry point"""
        try:
            # Start detection loop
            self.run_detection_loop()
            
        except Exception as e:
            print(f"Error in main application: {e}")
        finally:
            # Cleanup
            GPIO.cleanup()
            print("System shutdown complete")

# ESP32-specific implementation would go here
# For ESP32, you would create a separate class that uses machine module:
"""
class ESP32CarAccidentDetector:
    def __init__(self):
        from machine import Pin, Timer, I2C, UART
        from .sensors.mpu6050_esp32 import MPU6050_ESP32
        
        self.config = Config()
        self.setup_pins()
        
        # Initialize components
        self.i2c = I2C(0, scl=Pin(self.config.MPU6050_SCL_PIN), 
                      sda=Pin(self.config.MPU6050_SDA_PIN))
        self.mpu6050 = MPU6050_ESP32(self.i2c)
        self.sensor_fusion = SensorFusion()
        self.detector = AccidentDetector()
        self.sim7000c = SIM7000C_ESP32()
        
        # State variables
        self.accident_detected = False
        self.alert_timer = None
        self.system_active = True
        
        # Setup button interrupt
        self.button = Pin(self.config.BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)
        
        # Setup LED
        self.led = Pin(self.config.LED_PIN, Pin.OUT)
        self.led.off()
        
        # Initialize communications
        self.initialize_communications()
    
    def setup_pins(self):
        # ESP32 specific pin setup
        pass
        
    def button_pressed(self, pin):
        # Handle button press
        if self.accident_detected:
            self.cancel_alert()
    
    def read_sensors(self):
        # Read from MPU6050
        accel = self.mpu6050.get_acceleration()
        gyro = self.mpu6050.get_gyroscope()
        return accel, gyro
"""

if __name__ == "__main__":
    # Run with mock for testing
    detector = ESP32CarAccidentDetector(use_mock=True)
    detector.run()