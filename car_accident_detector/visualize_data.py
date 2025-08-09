#!/usr/bin/env python3
"""
Visualize sensor data in real-time
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from sensors.mpu6050 import MPU6050
import time

class SensorVisualizer:
    def __init__(self, max_points=200):
        self.max_points = max_points
        
        # Initialize sensor
        self.sensor = MPU6050()
        
        # Data buffers
        self.times = deque(maxlen=max_points)
        self.accel_x = deque(maxlen=max_points)
        self.accel_y = deque(maxlen=max_points)
        self.accel_z = deque(maxlen=max_points)
        self.gyro_x = deque(maxlen=max_points)
        self.gyro_y = deque(maxlen=max_points)
        self.gyro_z = deque(maxlen=max_points)
        
        # Setup plot
        self.fig, self.axes = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle('MPU6050 Sensor Data')
        
        # Initialize empty lines
        self.lines = []
        for i, ax in enumerate(self.axes):
            for j in range(3):
                line, = ax.plot([], [], label=['X', 'Y', 'Z'][j])
                self.lines.append(line)
        
        # Set up axes
        self.axes[0].set_ylabel('Acceleration (g)')
        self.axes[0].set_title('Accelerometer Data')
        self.axes[0].legend()
        self.axes[0].grid(True)
        
        self.axes[1].set_ylabel('Angular Velocity (°/s)')
        self.axes[1].set_xlabel('Time (s)')
        self.axes[1].set_title('Gyroscope Data')
        self.axes[1].legend()
        self.axes[1].grid(True)
        
        self.start_time = time.time()
        
    def update_plot(self, frame):
        # Read sensor data
        try:
            data = self.sensor.read_sensor_data()
        except Exception as e:
            print(f"Error reading sensor: {e}")
            return self.lines
        
        # Add data to buffers
        current_time = time.time() - self.start_time
        self.times.append(current_time)
        self.accel_x.append(data[0])
        self.accel_y.append(data[1])
        self.accel_z.append(data[2])
        self.gyro_x.append(data[3])
        self.gyro_y.append(data[4])
        self.gyro_z.append(data[5])
        
        # Update accelerometer plot
        self.lines[0].set_data(list(self.times), list(self.accel_x))
        self.lines[1].set_data(list(self.times), list(self.accel_y))
        self.lines[2].set_data(list(self.times), list(self.accel_z))
        
        # Update gyroscope plot
        self.lines[3].set_data(list(self.times), list(self.gyro_x))
        self.lines[4].set_data(list(self.times), list(self.gyro_y))
        self.lines[5].set_data(list(self.times), list(self.gyro_z))
        
        # Adjust plot limits
        if len(self.times) > 1:
            for ax in self.axes:
                ax.set_xlim(max(0, current_time - 10), current_time + 1)
            
            # Auto-scale y-axes
            accel_data = [self.accel_x, self.accel_y, self.accel_z]
            gyro_data = [self.gyro_x, self.gyro_y, self.gyro_z]
            
            accel_min = min([min(d) for d in accel_data if d])
            accel_max = max([max(d) for d in accel_data if d])
            if accel_min != accel_max:
                self.axes[0].set_ylim(accel_min - 0.5, accel_max + 0.5)
            
            gyro_min = min([min(d) for d in gyro_data if d])
            gyro_max = max([max(d) for d in gyro_data if d])
            if gyro_min != gyro_max:
                self.axes[1].set_ylim(gyro_min - 10, gyro_max + 10)
        
        return self.lines
    
    def start(self):
        ani = FuncAnimation(
            self.fig, 
            self.update_plot, 
            interval=50,  # Update every 50ms
            blit=False
        )
        
        plt.tight_layout()
        plt.show()

def main():
    print("Starting sensor visualization...")
    print("Press Ctrl+C to stop")
    
    try:
        visualizer = SensorVisualizer()
        visualizer.start()
    except KeyboardInterrupt:
        print("\nVisualization stopped")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()