import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import argparse

def load_and_preprocess_data(data_path):
    """
    Load and preprocess sensor data for training
    
    Args:
        data_path: Path to CSV file containing sensor data with labels
        
    Returns:
        X_train, X_test, y_train, y_test: Split and preprocessed data
    """
    # Load data
    data = pd.read_csv(data_path)
    
    # Assuming columns: timestamp, acceleration_x, acceleration_y, acceleration_z,
    # gyroscope_x, gyroscope_y, gyroscope_z, speed, label
    feature_columns = [
        'acceleration_x', 'acceleration_y', 'acceleration_z',
        'gyroscope_x', 'gyroscope_y', 'gyroscope_z', 'speed'
    ]
    
    # Extract features and labels
    X = data[feature_columns].values
    y = data['label'].values  # 1 for accident, 0 for normal
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Reshape for LSTM (samples, timesteps, features)
    # For simplicity, we'll treat each row as a single timestep sequence
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_reshaped, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save scaler for inference
    joblib.dump(scaler, 'scaler.pkl')
    
    return X_train, X_test, y_train, y_test

def create_model(input_shape):
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

def train_model(data_path, model_path='accident_detection_model.h5'):
    """
    Train the accident detection model
    
    Args:
        data_path: Path to training data CSV
        model_path: Path to save trained model
    """
    # Load and preprocess data
    X_train, X_test, y_train, y_test = load_and_preprocess_data(data_path)
    
    # Create model
    model = create_model((X_train.shape[1], X_train.shape[2]))
    
    # Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model_checkpoint = ModelCheckpoint(model_path, save_best_only=True)
    
    # Train model
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
    
    return model, history

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train accident detection model')
    parser.add_argument('--data', type=str, required=True, help='Path to training data CSV')
    parser.add_argument('--model', type=str, default='accident_detection_model.h5', 
                        help='Path to save trained model')
    
    args = parser.parse_args()
    
    print("Training accident detection model...")
    model, history = train_model(args.data, args.model)
    print(f"Model saved to {args.model}")