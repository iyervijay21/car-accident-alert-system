import serial
import time
from typing import Optional, Tuple
import pynmea2
from ..config import Config

class GPSInterface:
    """
    Interface for GPS module
    """
    
    def __init__(self):
        self.config = Config()
        self.serial_port = None
        self.last_position = None
        self.last_update = 0
        
    def connect(self) -> bool:
        """
        Connect to GPS module via serial
        Returns: True if connected successfully
        """
        try:
            self.serial_port = serial.Serial(
                self.config.SERIAL_PORT,
                self.config.BAUD_RATE,
                timeout=1
            )
            return True
        except Exception as e:
            print(f"Failed to connect to GPS: {e}")
            return False
    
    def get_position(self) -> Optional[Tuple[float, float]]:
        """
        Get current GPS position (latitude, longitude)
        Returns: (latitude, longitude) or None if unavailable
        """
        if not self.serial_port:
            return None
            
        try:
            # Read data for up to 1 second
            start_time = time.time()
            while time.time() - start_time < 1.0:
                line = self.serial_port.readline().decode('ascii', errors='replace')
                if line.startswith('$GPGGA'):
                    try:
                        msg = pynmea2.parse(line)
                        if msg.latitude and msg.longitude:
                            lat = float(msg.latitude)
                            lon = float(msg.longitude)
                            # Convert from DDMM.MMMM to DD.DDDDDD
                            lat = lat // 100 + (lat % 100) / 60
                            lon = lon // 100 + (lon % 100) / 60
                            # Apply sign based on direction
                            if msg.lat_dir == 'S':
                                lat = -lat
                            if msg.lon_dir == 'W':
                                lon = -lon
                            self.last_position = (lat, lon)
                            self.last_update = time.time()
                            return self.last_position
                    except pynmea2.ParseError:
                        continue
        except Exception as e:
            print(f"Error reading GPS data: {e}")
            
        return self.last_position
    
    def get_google_maps_link(self) -> Optional[str]:
        """
        Get Google Maps link for current position
        Returns: Google Maps URL or None if position unavailable
        """
        position = self.get_position()
        if position:
            lat, lon = position
            return f"https://www.google.com/maps?q={lat},{lon}"
        return None
    
    def is_valid_position(self) -> bool:
        """
        Check if we have a valid GPS position
        Returns: True if position is valid
        """
        if not self.last_position:
            return False
        # Check if position is less than 5 minutes old
        return (time.time() - self.last_update) < 300