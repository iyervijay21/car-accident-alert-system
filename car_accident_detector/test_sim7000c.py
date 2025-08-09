#!/usr/bin/env python3
"""
Test script for SIM7000C module
"""

import time
from alert.sim7000c import SIM7000C
from config import Config

def main():
    print("Testing SIM7000C module...")
    
    try:
        # Initialize module
        config = Config()
        sim7000c = SIM7000C()
        
        if not sim7000c.connect():
            print("Failed to connect to SIM7000C")
            return
            
        if not sim7000c.initialize_module():
            print("Failed to initialize SIM7000C")
            return
            
        print("SIM7000C initialized successfully")
        
        # Check signal strength
        signal = sim7000c.get_signal_strength()
        if signal:
            print(f"GSM signal strength: {signal} dBm")
        else:
            print("Could not read signal strength")
        
        # Test sending SMS (uncomment to actually send)
        # print("Sending test SMS...")
        # success = sim7000c.send_sms(config.PHONE_NUMBER, "Test message from car accident detector")
        # if success:
        #     print("Test SMS sent successfully")
        # else:
        #     print("Failed to send test SMS")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()