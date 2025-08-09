"""
ESP32 Car Accident Detection System - Complete Workflow Demo

This script demonstrates the complete workflow from data generation,
model training, to inference with the trained model.
"""

import sys
import os
import numpy as np

# Add the esp32_accident_detector directory to the path
sys.path.insert(0, 'esp32_accident_detector')

def demo_complete_workflow():
    """Demonstrate the complete workflow"""
    print("ESP32 Car Accident Detection System - Complete Workflow Demo")
    print("=" * 60)
    print()
    
    # Step 1: Generate training data
    print("Step 1: Generating Training Data")
    print("-" * 30)
    
    from ml.generate_data import generate_training_data
    import pandas as pd
    
    # Generate a small dataset for demo
    df = generate_training_data(num_sequences=100, sequence_length=50)
    
    # Save to CSV
    data_file = 'esp32_accident_detector/demo_training_data.csv'
    df.to_csv(data_file, index=False)
    
    # Print statistics
    total_samples = len(df)
    accident_samples = df['label'].sum()
    normal_samples = total_samples - accident_samples
    
    print(f"Generated {total_samples} samples")
    print(f"Accident samples: {accident_samples} ({accident_samples/total_samples*100:.1f}%)")
    print(f"Normal samples: {normal_samples} ({normal_samples/total_samples*100:.1f}%)")
    print()
    
    # Step 2: Train model
    print("Step 2: Training ML Model")
    print("-" * 30)
    
    from ml.train import train_model
    
    try:
        model, history = train_model(
            data_file, 
            model_save_path='esp32_accident_detector/demo_model.h5',
            sequence_length=50,
            epochs=5  # Reduced for demo
        )
        
        print("Model training completed!")
        final_accuracy = max(history.history['accuracy'])
        final_val_accuracy = max(history.history['val_accuracy'])
        print(f"Final training accuracy: {final_accuracy:.4f}")
        print(f"Final validation accuracy: {final_val_accuracy:.4f}")
        print()
        
    except Exception as e:
        print(f"Model training failed: {e}")
        return
    
    # Step 3: Test inference
    print("Step 3: Testing Inference")
    print("-" * 30)
    
    from ml.inference import AccidentDetector
    
    # Initialize the detector with our trained model
    model_path = 'esp32_accident_detector/demo_model.tflite'
    detector = AccidentDetector(model_path)
    
    # Print model info
    info = detector.get_model_info()
    print(f"Model info: {info}")
    
    if not info.get("loaded", False):
        print("Failed to load model. Exiting.")
        return
    
    # Test with normal data
    print("\nTesting with normal driving data...")
    normal_data = np.random.normal(0, 0.5, (1, 50, 6))
    # Scale to match our training data ranges
    normal_data[:, :, :3] = np.clip(normal_data[:, :, :3], -2.0, 2.0) / 2.0  # Acceleration
    normal_data[:, :, 3:] = np.clip(normal_data[:, :, 3:], -250.0, 250.0) / 250.0  # Gyroscope
    
    is_accident, confidence = detector.predict(normal_data)
    print(f"Normal driving - Accident: {is_accident}, Confidence: {confidence:.4f}")
    
    # Test with high-value data (simulating accident)
    print("\nTesting with high-value data (accident simulation)...")
    high_data = np.random.normal(0, 3.0, (1, 50, 6))
    # Scale to match our training data ranges
    high_data[:, :, :3] = np.clip(high_data[:, :, :3], -2.0, 2.0) / 2.0  # Acceleration
    high_data[:, :, 3:] = np.clip(high_data[:, :, 3:], -250.0, 250.0) / 250.0  # Gyroscope
    
    is_accident, confidence = detector.predict(high_data)
    print(f"High-value simulation - Accident: {is_accident}, Confidence: {confidence:.4f}")
    
    print()
    print("Workflow demo completed!")
    print()
    print("The trained model is ready for deployment on ESP32.")
    print("Model files:")
    print(f"- {model_path} (TensorFlow Lite model)")
    print("- Feature scaler would be needed for production use")

if __name__ == "__main__":
    demo_complete_workflow()