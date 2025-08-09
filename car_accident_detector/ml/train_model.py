import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import tensorflow as tf
import os

def load_and_preprocess_data(data_path: str):
    """
    Load and preprocess sensor data for training
    Expected CSV columns: timestamp, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, label
    """
    # Load data
    df = pd.read_csv(data_path)
    
    # Extract features and labels
    feature_columns = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
    X = df[feature_columns].values
    y = df['label'].values  # 1 for accident, 0 for normal
    
    # Reshape data into sequences (assuming 50 samples per sequence)
    sequence_length = 50
    X_sequences = []
    y_sequences = []
    
    for i in range(len(X) - sequence_length + 1):
        X_sequences.append(X[i:i+sequence_length])
        # For sequence labeling, we can take the max label in the sequence
        y_sequences.append(np.max(y[i:i+sequence_length]))
    
    X_sequences = np.array(X_sequences)
    y_sequences = np.array(y_sequences)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_sequences, y_sequences, test_size=0.2, random_state=42, stratify=y_sequences
    )
    
    return X_train, X_test, y_train, y_test

def create_lstm_model(input_shape):
    """
    Create LSTM model for accident detection
    """
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def create_cnn_model(input_shape):
    """
    Create 1D CNN model for accident detection
    """
    model = Sequential([
        tf.keras.layers.Conv1D(32, 3, activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(64, 3, activation='relu'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(128, 3, activation='relu'),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model(data_path: str, model_type: str = 'lstm', model_save_path: str = 'accident_model.h5'):
    """
    Train accident detection model
    """
    print("Loading and preprocessing data...")
    X_train, X_test, y_train, y_test = load_and_preprocess_data(data_path)
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")
    
    # Create model
    input_shape = (X_train.shape[1], X_train.shape[2])
    if model_type == 'lstm':
        model = create_lstm_model(input_shape)
        print("Created LSTM model")
    else:
        model = create_cnn_model(input_shape)
        print("Created CNN model")
    
    # Print model summary
    model.summary()
    
    # Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    model_checkpoint = ModelCheckpoint(model_save_path, save_best_only=True)
    
    # Train model
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping, model_checkpoint],
        verbose=1
    )
    
    # Evaluate model
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy: {test_accuracy:.4f}")
    
    # Convert to TensorFlow Lite for embedded deployment
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    tflite_path = model_save_path.replace('.h5', '.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"Model saved as {model_save_path}")
    print(f"TensorFlow Lite model saved as {tflite_path}")
    
    return model, history

def generate_sample_data(filename: str = 'sample_data.csv', samples: int = 10000):
    """
    Generate sample training data for testing
    """
    np.random.seed(42)
    
    data = []
    for i in range(samples):
        # Determine if this is an accident sample (10% of data)
        is_accident = np.random.random() < 0.1
        
        if is_accident:
            # Accident data - higher acceleration/gyroscope values
            accel_x = np.random.normal(0, 3.0)  # Higher variance
            accel_y = np.random.normal(0, 3.0)
            accel_z = np.random.normal(0, 3.0)
            gyro_x = np.random.normal(0, 100.0)
            gyro_y = np.random.normal(0, 100.0)
            gyro_z = np.random.normal(0, 100.0)
        else:
            # Normal driving data
            accel_x = np.random.normal(0, 0.5)
            accel_y = np.random.normal(0, 0.5)
            accel_z = np.random.normal(1.0, 0.5)  # Gravity on Z-axis
            gyro_x = np.random.normal(0, 10.0)
            gyro_y = np.random.normal(0, 10.0)
            gyro_z = np.random.normal(0, 10.0)
        
        data.append({
            'timestamp': i,
            'accel_x': accel_x,
            'accel_y': accel_y,
            'accel_z': accel_z,
            'gyro_x': gyro_x,
            'gyro_y': gyro_y,
            'gyro_z': gyro_z,
            'label': 1 if is_accident else 0
        })
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Generated {samples} samples with {np.sum(df['label'])} accidents")
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train accident detection model')
    parser.add_argument('--data', type=str, help='Path to training data CSV')
    parser.add_argument('--model_type', type=str, default='lstm', 
                        choices=['lstm', 'cnn'], help='Model type to train')
    parser.add_argument('--output', type=str, default='accident_model.h5',
                        help='Output model file path')
    parser.add_argument('--generate_sample', action='store_true',
                        help='Generate sample data for testing')
    
    args = parser.parse_args()
    
    if args.generate_sample:
        generate_sample_data()
    elif args.data:
        train_model(args.data, args.model_type, args.output)
    else:
        print("Please provide either --data or --generate_sample argument")
        parser.print_help()