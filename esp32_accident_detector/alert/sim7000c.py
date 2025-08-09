import time
from typing import Optional
import serial
from config import Config

class SIM7000C:
    """
    Interface for SIM7000C GSM/GPS module optimized for ESP32
    """
    
    def __init__(self):
        self.config = Config()
        self.serial_port = None
        self.initialized = False
        self.power_pin = None  # For ESP32 power control if needed
        
    def connect(self) -> bool:
        """
        Connect to SIM7000C module via serial
        Returns: True if connected successfully
        """
        try:
            # For ESP32, we might need to use a different serial implementation
            # This is a simplified version - actual ESP32 implementation would
            # use machine.UART or similar
            
            # In a real ESP32 implementation, you would use:
            # from machine import UART, Pin
            # self.serial_port = UART(1, baudrate=self.config.BAUD_RATE, 
            #                        tx=Pin(self.config.SIM7000C_TX_PIN), 
            #                        rx=Pin(self.config.SIM7000C_RX_PIN))
            
            # For PC testing, we'll use pyserial
            self.serial_port = serial.Serial(
                self.config.SERIAL_PORT,
                self.config.BAUD_RATE,
                timeout=2
            )
            print("Connected to SIM7000C")
            return True
        except Exception as e:
            print(f"Failed to connect to SIM7000C: {e}")
            return False
    
    def send_at_command(self, command: str, wait_time: float = 1.0) -> str:
        """
        Send AT command to SIM7000C and return response
        """
        if not self.serial_port:
            return ""
            
        try:
            # Clear input buffer
            self.serial_port.flushInput()
            
            # Send command
            cmd = command + '\r\n'
            self.serial_port.write(cmd.encode())
            time.sleep(wait_time)
            
            # Read response
            response = ""
            start_time = time.time()
            while time.time() - start_time < 2.0:
                if self.serial_port.in_waiting > 0:
                    response += self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                time.sleep(0.1)
            
            return response
        except Exception as e:
            print(f"Error sending AT command: {e}")
            return ""
    
    def initialize_module(self) -> bool:
        """
        Initialize SIM7000C module
        Returns: True if initialization successful
        """
        if not self.serial_port:
            return False
            
        print("Initializing SIM7000C...")
        
        # Test communication
        response = self.send_at_command("AT", 1)
        if "OK" not in response:
            print("Module not responding to AT commands")
            return False
        
        # Set SMS mode to text
        self.send_at_command("AT+CMGF=1", 1)
        
        # Set SMS character set
        self.send_at_command("AT+CSCS=\"GSM\"", 1)
        
        # Enable SMS notification
        self.send_at_command("AT+CNMI=1,2,0,0,0", 1)
        
        # Check if SIM is inserted and registered
        response = self.send_at_command("AT+CPIN?", 1)
        if "READY" not in response:
            print("SIM card not ready")
            return False
        
        response = self.send_at_command("AT+CREG?", 1)
        if "+CREG: 0,1" not in response and "+CREG: 0,5" not in response:
            print("Not registered to network")
            return False
        
        print("SIM7000C initialized successfully")
        self.initialized = True
        return True
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS message
        Returns: True if sent successfully
        """
        if not self.initialized:
            print("Module not initialized")
            return False
            
        try:
            # Send SMS command
            self.send_at_command(f"AT+CMGS=\"{phone_number}\"", 1)
            
            # Send message content
            self.serial_port.write(message.encode())
            
            # Send Ctrl+Z to terminate message
            self.serial_port.write(b'\x1A')
            
            # Wait for response
            time.sleep(3)
            
            response = self.serial_port.read_all().decode('utf-8', errors='ignore')
            if "OK" in response or "+CMGS" in response:
                print(f"SMS sent successfully to {phone_number}")
                return True
            else:
                print(f"Failed to send SMS to {phone_number}")
                print(f"Response: {response}")
                return False
                
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def send_alert(self, phone_number: str, location_link: Optional[str] = None) -> bool:
        """
        Send accident alert SMS
        """
        if location_link:
            message = f"EMERGENCY: Car accident detected! Location: {location_link}"
        else:
            message = "EMERGENCY: Car accident detected! Location unknown."
        
        print(f"Sending alert: {message}")
        return self.send_sms(phone_number, message)
    
    def get_signal_strength(self) -> Optional[int]:
        """
        Get network signal strength
        Returns: Signal strength in dBm or None if unavailable
        """
        response = self.send_at_command("AT+CSQ", 1)
        if "+CSQ:" in response:
            try:
                # Parse response like "+CSQ: 15,0"
                parts = response.split("+CSQ:")[1].split(",")[0].strip()
                signal = int(parts)
                # Convert to dBm (approximate)
                dBm = -113 + (signal * 2)
                return dBm
            except:
                pass
        return None
    
    def get_gps_location(self) -> Optional[tuple]:
        """
        Get GPS location from SIM7000C module
        Returns: (latitude, longitude) or None if unavailable
        """
        try:
            # Enable GPS
            self.send_at_command("AT+CGNSPWR=1", 1)
            
            # Get GPS info
            response = self.send_at_command("AT+CGNSINF", 2)
            
            if "+CGNSINF:" in response:
                # Parse GPS response
                # Format: +CGNSINF: <type>,<fix>,<lat>,<lon>,<alt>,...
                parts = response.split("+CGNSINF:")[1].split("\n")[0].split(",")
                if len(parts) > 4 and parts[1] == "1":  # Fix valid
                    lat = float(parts[2]) if parts[2] else 0.0
                    lon = float(parts[3]) if parts[3] else 0.0
                    return (lat, lon)
        except Exception as e:
            print(f"Error getting GPS location: {e}")
        
        return None
    
    def get_google_maps_link(self, lat: float, lon: float) -> str:
        """
        Generate Google Maps link for coordinates
        """
        return f"https://www.google.com/maps?q={lat},{lon}"

# Mock implementation for testing without hardware
class MockSIM7000C:
    """
    Mock SIM7000C implementation for testing
    """
    
    def __init__(self):
        self.config = Config()
        self.initialized = False
        print("Using Mock SIM7000C for testing")
    
    def connect(self) -> bool:
        print("Mock: Connected to SIM7000C")
        return True
    
    def initialize_module(self) -> bool:
        print("Mock: SIM7000C initialized")
        self.initialized = True
        return True
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        print(f"Mock SMS sent to {phone_number}: {message}")
        return True
    
    def send_alert(self, phone_number: str, location_link: Optional[str] = None) -> bool:
        if location_link:
            message = f"EMERGENCY: Car accident detected! Location: {location_link}"
        else:
            message = "EMERGENCY: Car accident detected! Location unknown."
        return self.send_sms(phone_number, message)
    
    def get_signal_strength(self) -> Optional[int]:
        return -75  # Good signal strength
    
    def get_gps_location(self) -> Optional[tuple]:
        # Return a mock location (New York City)
        return (40.7128, -74.0060)
    
    def get_google_maps_link(self, lat: float, lon: float) -> str:
        return f"https://www.google.com/maps?q={lat},{lon}"