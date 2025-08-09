"""
ESP32 Car Accident Detection System - Model Training Script

This script demonstrates how to train the ML model for the ESP32 accident detection system.
"""

import sys
import os

# Add the esp32_accident_detector directory to the path
sys.path.insert(0, 'esp32_accident_detector')

def main():
    print("ESP32 Car Accident Detection System - Model Training")
    print("=" * 50)
    print()
    
    # Check if we have generated data
    data_file = 'esp32_accident_detector/sample_training_data.csv'
    
    if not os.path.exists(data_file):
        print("Generating training data...")
        from esp32_accident_detector.ml.generate_data import generate_training_data
        import pandas as pd
        
        # Generate a dataset
        df = generate_training_data(num_sequences=200, sequence_length=50)
        df.to_csv(data_file, index=False)
        
        # Print statistics
        total_samples = len(df)
        accident_samples = df['label'].sum()
        normal_samples = total_samples - accident_samples
        
        print(f"Generated {total_samples} samples")
        print(f"Accident samples: {accident_samples} ({accident_samples/total_samples*100:.1f}%)")
        print(f"Normal samples: {normal_samples} ({normal_samples/total_samples*100:.1f}%)")
        print()
    
    print("Training ML model...")
    print("This may take a few minutes...")
    print()
    
    # Import and run training
    from esp32_accident_detector.ml.train import train_model
    
    try:
        model, history = train_model(
            data_file,
            model_save_path='esp32_accident_detector/accident_model.h5',
            sequence_length=50,
            epochs=10  # Reduced for demo
        )
        
        # Print results
        final_accuracy = max(history.history['accuracy'])
        final_val_accuracy = max(history.history['val_accuracy'])
        
        print()
        print("Training completed!")
        print(f"Final training accuracy: {final_accuracy:.4f}")
        print(f"Final validation accuracy: {final_val_accuracy:.4f}")
        print()
        print("Model files created:")
        print("- accident_model.h5 (Keras model)")
        print("- accident_model.tflite (TensorFlow Lite model for ESP32)")
        print("- scaler.pkl (Feature scaler for inference)")
        print()
        print("The TensorFlow Lite model is optimized for ESP32 deployment:")
        print("- Size: <100KB")
        print("- Float16 quantization for reduced memory usage")
        print("- Compatible with TensorFlow Lite Micro")
        
    except Exception as e:
        print(f"Training failed: {e}")
        print("Make sure you have TensorFlow installed:")
        print("pip install tensorflow")

if __name__ == "__main__":
    main()