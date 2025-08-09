import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import argparse
import os

def load_and_preprocess_data(data_path: str, sequence_length: int = 50):
    """
    Load and preprocess sensor data for training
    Expected CSV columns: timestamp, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, label
    """
    print("Loading data...")
    # Load data
    df = pd.read_csv(data_path)
    
    # Extract features and labels
    feature_columns = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
    X = df[feature_columns].values
    y = df['label'].values  # 1 for accident, 0 for normal
    
    print(f"Total samples: {len(X)}")
    print(f"Accident samples: {np.sum(y)}")
    print(f"Normal samples: {len(y) - np.sum(y)}")
    
    # Reshape data into sequences
    X_sequences = []
    y_sequences = []
    
    for i in range(len(X) - sequence_length + 1):
        X_sequences.append(X[i:i+sequence_length])
        # For sequence labeling, we can take the max label in the sequence
        y_sequences.append(np.max(y[i:i+sequence_length]))
    
    X_sequences = np.array(X_sequences)
    y_sequences = np.array(y_sequences)
    
    print(f"Sequences created: {len(X_sequences)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_sequences, y_sequences, test_size=0.2, random_state=42, stratify=y_sequences
    )
    
    # Normalize features
    # Reshape for normalization (samples*timesteps, features)
    X_train_reshaped = X_train.reshape(-1, X_train.shape[2])
    X_test_reshaped = X_test.reshape(-1, X_test.shape[2])
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_reshaped)
    X_test_scaled = scaler.transform(X_test_reshaped)
    
    # Reshape back to (samples, timesteps, features)
    X_train = X_train_scaled.reshape(X_train.shape)
    X_test = X_test_scaled.reshape(X_test.shape)
    
    # Save scaler for inference
    import joblib
    joblib.dump(scaler, 'scaler.pkl')
    print("Scaler saved as scaler.pkl")
    
    return X_train, X_test, y_train, y_test

def create_lightweight_lstm_model(input_shape, units=[32, 16], dropout=0.2):
    """
    Create a lightweight LSTM model optimized for embedded deployment
    """
    model = Sequential()
    
    # First LSTM layer
    model.add(LSTM(units[0], return_sequences=len(units) > 1, input_shape=input_shape))
    if dropout > 0:
        model.add(Dropout(dropout))
    
    # Additional LSTM layers if specified
    for i in range(1, len(units)):
        return_sequences = (i < len(units) - 1)
        model.add(LSTM(units[i], return_sequences=return_sequences))
        if dropout > 0:
            model.add(Dropout(dropout))
    
    # Dense layers
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model(data_path: str, model_save_path: str = 'accident_model.h5', 
                sequence_length: int = 50, epochs: int = 50):
    """
    Train lightweight accident detection model
    """
    print("Loading and preprocessing data...")
    X_train, X_test, y_train, y_test = load_and_preprocess_data(data_path, sequence_length)
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")
    
    # Create lightweight model
    input_shape = (X_train.shape[1], X_train.shape[2])
    model = create_lightweight_lstm_model(input_shape, units=[32, 16], dropout=0.2)
    
    print("Model architecture:")
    model.summary()
    
    # Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    model_checkpoint = ModelCheckpoint(model_save_path, save_best_only=True)
    
    # Train model
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping, model_checkpoint],
        verbose=1
    )
    
    # Evaluate model
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Test Loss: {test_loss:.4f}")
    
    # Convert to TensorFlow Lite for embedded deployment
    print("Converting to TensorFlow Lite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Enable float16 quantization for additional size reduction
    converter.target_spec.supported_types = [tf.float16]
    
    # Handle LSTM conversion issues
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    converter._experimental_lower_tensor_list_ops = False
    
    try:
        tflite_model = converter.convert()
        
        tflite_path = model_save_path.replace('.h5', '.tflite')
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"Model saved as {model_save_path}")
        print(f"TensorFlow Lite model saved as {tflite_path}")
        print(f"TFLite model size: {len(tflite_model) / 1024:.1f} KB")
    except Exception as e:
        print(f"Failed to convert to TensorFlow Lite: {e}")
        print("Model saved as Keras model only")
        print(f"Model saved as {model_save_path}")
    
    return model, history

def generate_sample_data(filename: str = 'sample_data.csv', samples: int = 10000):
    """
    Generate sample training data for testing
    """
    np.random.seed(42)
    
    # Generate more realistic sample data with patterns
    data = []
    
    for i in range(samples):
        # Determine if this is an accident sample (10% of data)
        is_accident = np.random.random() < 0.1
        
        if is_accident:
            # Simulate accident pattern - sudden high acceleration/gyro changes
            # Start with normal data
            accel_x = np.random.normal(0, 0.5)
            accel_y = np.random.normal(0, 0.5)
            accel_z = np.random.normal(1.0, 0.5)
            gyro_x = np.random.normal(0, 10.0)
            gyro_y = np.random.normal(0, 10.0)
            gyro_z = np.random.normal(0, 10.0)
            
            # Add accident spike in the middle of sequence
            if i % 50 > 20 and i % 50 < 30:  # In the middle of a 50-sample sequence
                accel_x += np.random.normal(0, 3.0)
                accel_y += np.random.normal(0, 3.0)
                accel_z += np.random.normal(0, 3.0)
                gyro_x += np.random.normal(0, 100.0)
                gyro_y += np.random.normal(0, 100.0)
                gyro_z += np.random.normal(0, 100.0)
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
    parser = argparse.ArgumentParser(description='Train lightweight accident detection model')
    parser.add_argument('--data', type=str, help='Path to training data CSV')
    parser.add_argument('--output', type=str, default='accident_model.h5',
                        help='Output model file path')
    parser.add_argument('--sequence_length', type=int, default=50,
                        help='Sequence length for LSTM (default: 50)')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs (default: 50)')
    parser.add_argument('--generate_sample', action='store_true',
                        help='Generate sample data for testing')
    
    args = parser.parse_args()
    
    if args.generate_sample:
        generate_sample_data()
    elif args.data:
        train_model(args.data, args.output, args.sequence_length, args.epochs)
    else:
        print("Please provide either --data or --generate_sample argument")
        parser.print_help()