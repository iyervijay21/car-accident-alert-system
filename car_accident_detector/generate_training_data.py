import numpy as np
import pandas as pd
import time
from typing import List, Tuple
import argparse

def generate_normal_driving_data(duration_seconds: int = 3600, sampling_rate: int = 50) -> List[Tuple]:
    """
    Generate normal driving data
    """
    samples = duration_seconds * sampling_rate
    data = []
    
    for i in range(samples):
        # Simulate normal driving patterns
        time_sec = i / sampling_rate
        
        # Acceleration with small random variations and periodic patterns
        accel_x = np.random.normal(0, 0.3) + 0.2 * np.sin(2 * np.pi * time_sec / 10)
        accel_y = np.random.normal(0, 0.3) + 0.1 * np.cos(2 * np.pi * time_sec / 15)
        accel_z = np.random.normal(1.0, 0.2)  # Gravity on Z-axis
        
        # Gyroscope with small variations
        gyro_x = np.random.normal(0, 5.0)
        gyro_y = np.random.normal(0, 5.0)
        gyro_z = np.random.normal(0, 3.0)
        
        data.append((accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, 0))  # Label 0 for normal
    
    return data

def generate_accident_data(start_time: int, duration: int = 5, sampling_rate: int = 50) -> List[Tuple]:
    """
    Generate accident data with high acceleration/gyro values
    """
    samples = duration * sampling_rate
    data = []
    
    for i in range(samples):
        time_offset = i / sampling_rate
        
        # High acceleration values during accident
        accel_x = np.random.normal(0, 3.0) + 5.0 * np.exp(-time_offset * 5)
        accel_y = np.random.normal(0, 3.0) + 3.0 * np.exp(-time_offset * 3)
        accel_z = np.random.normal(0, 4.0) + 2.0 * np.exp(-time_offset * 4)
        
        # High gyroscope values during accident
        gyro_x = np.random.normal(0, 100.0) + 200.0 * np.exp(-time_offset * 2)
        gyro_y = np.random.normal(0, 100.0) + 150.0 * np.exp(-time_offset * 2)
        gyro_z = np.random.normal(0, 80.0) + 100.0 * np.exp(-time_offset * 2)
        
        data.append((accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, 1))  # Label 1 for accident
    
    return data

def create_training_dataset(hours_normal: int = 10, num_accidents: int = 20) -> pd.DataFrame:
    """
    Create a complete training dataset
    """
    all_data = []
    
    # Generate normal driving data
    print(f"Generating {hours_normal} hours of normal driving data...")
    normal_data = generate_normal_driving_data(hours_normal * 3600)
    all_data.extend(normal_data)
    
    # Insert accident events at random positions
    print(f"Inserting {num_accidents} accident events...")
    normal_samples = len(normal_data)
    
    for i in range(num_accidents):
        # Choose random position for accident
        accident_position = np.random.randint(1000, normal_samples - 1000)
        
        # Generate accident data
        accident_data = generate_accident_data(accident_position)
        
        # Insert accident data into normal data
        for j, accident_sample in enumerate(accident_data):
            if accident_position + j < len(all_data):
                all_data[accident_position + j] = accident_sample
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data, columns=[
        'accel_x', 'accel_y', 'accel_z',
        'gyro_x', 'gyro_y', 'gyro_z',
        'label'
    ])
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Generate training data for accident detection')
    parser.add_argument('--hours', type=int, default=10, help='Hours of normal driving data')
    parser.add_argument('--accidents', type=int, default=20, help='Number of accident events')
    parser.add_argument('--output', type=str, default='training_data.csv', help='Output CSV file')
    
    args = parser.parse_args()
    
    print("Generating training data...")
    df = create_training_dataset(args.hours, args.accidents)
    
    # Save to CSV
    df.to_csv(args.output, index=False)
    print(f"Generated {len(df)} samples with {df['label'].sum()} accident samples")
    print(f"Data saved to {args.output}")
    
    # Print dataset statistics
    print("\nDataset Statistics:")
    print(f"Total samples: {len(df)}")
    print(f"Normal samples: {len(df) - df['label'].sum()}")
    print(f"Accident samples: {df['label'].sum()}")
    print(f"Accident ratio: {df['label'].mean():.3f}")

if __name__ == "__main__":
    main()