import numpy as np
import pandas as pd
import argparse
from typing import List, Tuple
import time

def generate_realistic_accident_data(sequence_length: int = 50) -> List[Tuple[float, float, float, float, float, float, int]]:
    """
    Generate realistic accident data with sudden changes
    """
    data = []
    
    # Start with normal driving
    for i in range(sequence_length // 3):
        accel_x = np.random.normal(0, 0.3)
        accel_y = np.random.normal(0, 0.3)
        accel_z = np.random.normal(1.0, 0.3)  # Gravity
        gyro_x = np.random.normal(0, 5.0)
        gyro_y = np.random.normal(0, 5.0)
        gyro_z = np.random.normal(0, 5.0)
        data.append((accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, 0))
    
    # Accident event - sudden high values
    accident_start = sequence_length // 3
    accident_duration = sequence_length // 3
    
    for i in range(accident_start, accident_start + accident_duration):
        # Very high acceleration and gyroscope values during accident
        accel_x = np.random.normal(0, 4.0) + np.random.choice([-5, 5]) * np.random.random()
        accel_y = np.random.normal(0, 4.0) + np.random.choice([-5, 5]) * np.random.random()
        accel_z = np.random.normal(0, 4.0) + np.random.choice([-5, 5]) * np.random.random()
        gyro_x = np.random.normal(0, 150.0) + np.random.choice([-300, 300]) * np.random.random()
        gyro_y = np.random.normal(0, 150.0) + np.random.choice([-300, 300]) * np.random.random()
        gyro_z = np.random.normal(0, 150.0) + np.random.choice([-300, 300]) * np.random.random()
        data.append((accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, 1))
    
    # Recovery phase - values returning to normal
    recovery_start = accident_start + accident_duration
    for i in range(recovery_start, sequence_length):
        # Gradually return to normal values
        factor = (sequence_length - i) / (sequence_length - recovery_start)
        accel_x = np.random.normal(0, 0.3) * factor
        accel_y = np.random.normal(0, 0.3) * factor
        accel_z = np.random.normal(1.0, 0.3) * factor + 1.0 * (1 - factor)
        gyro_x = np.random.normal(0, 5.0) * factor
        gyro_y = np.random.normal(0, 5.0) * factor
        gyro_z = np.random.normal(0, 5.0) * factor
        data.append((accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, 1 if factor > 0.5 else 0))
    
    return data

def generate_normal_driving_data(sequence_length: int = 50) -> List[Tuple[float, float, float, float, float, float, int]]:
    """
    Generate normal driving data
    """
    data = []
    
    for i in range(sequence_length):
        accel_x = np.random.normal(0, 0.5)
        accel_y = np.random.normal(0, 0.5)
        accel_z = np.random.normal(1.0, 0.5)  # Gravity on Z-axis
        gyro_x = np.random.normal(0, 10.0)
        gyro_y = np.random.normal(0, 10.0)
        gyro_z = np.random.normal(0, 10.0)
        data.append((accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, 0))
    
    return data

def generate_training_data(num_sequences: int = 1000, sequence_length: int = 50) -> pd.DataFrame:
    """
    Generate training data for accident detection model
    """
    all_data = []
    
    for i in range(num_sequences):
        # 20% accident sequences, 80% normal sequences
        if np.random.random() < 0.2:
            sequence_data = generate_realistic_accident_data(sequence_length)
        else:
            sequence_data = generate_normal_driving_data(sequence_length)
        
        # Add timestamp
        timestamp_base = time.time() + i * sequence_length * 0.02  # 50Hz sampling
        
        for j, (ax, ay, az, gx, gy, gz, label) in enumerate(sequence_data):
            timestamp = timestamp_base + j * 0.02
            all_data.append({
                'timestamp': timestamp,
                'accel_x': ax,
                'accel_y': ay,
                'accel_z': az,
                'gyro_x': gx,
                'gyro_y': gy,
                'gyro_z': gz,
                'label': label
            })
    
    return pd.DataFrame(all_data)

def main():
    parser = argparse.ArgumentParser(description='Generate training data for accident detection')
    parser.add_argument('--sequences', type=int, default=1000, 
                        help='Number of sequences to generate (default: 1000)')
    parser.add_argument('--length', type=int, default=50,
                        help='Sequence length (default: 50)')
    parser.add_argument('--output', type=str, default='training_data.csv',
                        help='Output CSV file (default: training_data.csv)')
    
    args = parser.parse_args()
    
    print(f"Generating {args.sequences} sequences of length {args.length}...")
    
    df = generate_training_data(args.sequences, args.length)
    
    # Save to CSV
    df.to_csv(args.output, index=False)
    
    # Print statistics
    total_samples = len(df)
    accident_samples = df['label'].sum()
    normal_samples = total_samples - accident_samples
    
    print(f"Generated {total_samples} samples")
    print(f"Accident samples: {accident_samples} ({accident_samples/total_samples*100:.1f}%)")
    print(f"Normal samples: {normal_samples} ({normal_samples/total_samples*100:.1f}%)")
    print(f"Data saved to {args.output}")

if __name__ == "__main__":
    main()