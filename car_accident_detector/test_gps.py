#!/usr/bin/env python3
"""
Test script for GPS module
"""

import time
from sensors.gps import GPSInterface

def main():
    print("Testing GPS module...")
    
    try:
        # Initialize GPS
        gps = GPSInterface()
        
        if not gps.connect():
            print("Failed to connect to GPS")
            return
            
        print("GPS connected successfully")
        print("Waiting for GPS fix (press Ctrl+C to stop)...")
        print("Time\t\t\tLatitude\tLongitude\tLink")
        print("-" * 60)
        
        for i in range(30):  # Try for 30 seconds
            position = gps.get_position()
            link = gps.get_google_maps_link()
            
            if position:
                lat, lon = position
                print(f"{time.strftime('%H:%M:%S')}\t{lat:.6f}\t\t{lon:.6f}\t\t{link or 'N/A'}")
            else:
                print(f"{time.strftime('%H:%M:%S')}\tNo GPS fix")
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()