#!/usr/bin/env python3
"""
Convert TensorFlow model to TensorFlow Lite format
"""

import tensorflow as tf
import argparse
import os

def convert_model(input_path, output_path):
    """
    Convert TensorFlow model to TensorFlow Lite format
    """
    try:
        # Load the TensorFlow model
        print(f"Loading model from {input_path}...")
        model = tf.keras.models.load_model(input_path)
        
        # Convert to TensorFlow Lite
        print("Converting to TensorFlow Lite...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Apply optimizations
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Convert the model
        tflite_model = converter.convert()
        
        # Save the TensorFlow Lite model
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"Model converted successfully!")
        print(f"Output saved to {output_path}")
        
        # Print model information
        interpreter = tf.lite.Interpreter(model_path=output_path)
        interpreter.allocate_tensors()
        
        # Get input and output tensors
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print("\nModel Details:")
        print(f"Input shape: {input_details[0]['shape']}")
        print(f"Input type: {input_details[0]['dtype']}")
        print(f"Output shape: {output_details[0]['shape']}")
        print(f"Output type: {output_details[0]['dtype']}")
        
        # Get model size
        model_size = os.path.getsize(output_path)
        print(f"Model size: {model_size / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"Error converting model: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert TensorFlow model to TensorFlow Lite')
    parser.add_argument('--input', type=str, required=True, help='Input TensorFlow model file (.h5)')
    parser.add_argument('--output', type=str, default='model.tflite', help='Output TensorFlow Lite file')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found")
        return
    
    # Convert model
    success = convert_model(args.input, args.output)
    
    if success:
        print("\nConversion completed successfully!")
    else:
        print("\nConversion failed!")

if __name__ == "__main__":
    main()