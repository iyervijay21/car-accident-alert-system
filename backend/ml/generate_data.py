import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(num_samples=1000, accident_ratio=0.1):
    """
    Generate sample sensor data for training
    
    Args:
        num_samples: Number of samples to generate
        accident_ratio: Ratio of samples that represent accidents
        
    Returns:
        DataFrame with sensor data and labels
    """
    data = []
    
    for i in range(num_samples):
        # Determine if this is an accident sample
        is_accident = random.random() < accident_ratio
        
        # Generate base sensor values
        if is_accident:
            # Accident data - higher acceleration/gyroscope values
            acceleration_x = random.uniform(-5.0, 5.0)
            acceleration_y = random.uniform(-5.0, 5.0)
            acceleration_z = random.uniform(-5.0, 5.0)
            gyroscope_x = random.uniform(-3.0, 3.0)
            gyroscope_y = random.uniform(-3.0, 3.0)
            gyroscope_z = random.uniform(-3.0, 3.0)
            speed = random.uniform(20.0, 120.0)
        else:
            # Normal driving data
            acceleration_x = random.uniform(-2.0, 2.0)
            acceleration_y = random.uniform(-2.0, 2.0)
            acceleration_z = random.uniform(-2.0, 2.0)
            gyroscope_x = random.uniform(-1.0, 1.0)
            gyroscope_y = random.uniform(-1.0, 1.0)
            gyroscope_z = random.uniform(-1.0, 1.0)
            speed = random.uniform(0.0, 100.0)
        
        # Add timestamp
        timestamp = datetime.now() - timedelta(seconds=random.randint(0, 86400))
        
        data.append({
            'timestamp': timestamp,
            'acceleration_x': acceleration_x,
            'acceleration_y': acceleration_y,
            'acceleration_z': acceleration_z,
            'gyroscope_x': gyroscope_x,
            'gyroscope_y': gyroscope_y,
            'gyroscope_z': gyroscope_z,
            'speed': speed,
            'label': 1 if is_accident else 0
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Generate sample training data
    print("Generating sample training data...")
    df = generate_sample_data(5000, 0.15)  # 5000 samples, 15% accidents
    
    # Save to CSV
    df.to_csv('sample_training_data.csv', index=False)
    print(f"Generated {len(df)} samples ({df['label'].sum()} accidents)")
    print("Data saved to sample_training_data.csv")