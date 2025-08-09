import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import numpy as np

def create_accident_detection_model(input_shape):
    """
    Create an LSTM model for car accident detection
    
    Args:
        input_shape: Tuple representing the shape of input data (timesteps, features)
        
    Returns:
        Compiled Keras model
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

def preprocess_sensor_data(data):
    """
    Preprocess sensor data for model input
    
    Args:
        data: List of dictionaries containing sensor readings
        
    Returns:
        Normalized numpy array ready for model input
    """
    # Extract features
    features = []
    for reading in data:
        features.append([
            reading['acceleration_x'],
            reading['acceleration_y'],
            reading['acceleration_z'],
            reading['gyroscope_x'],
            reading['gyroscope_y'],
            reading['gyroscope_z'],
            reading.get('speed', 0)
        ])
    
    # Convert to numpy array
    features = np.array(features)
    
    # Normalize features (you would use precomputed normalization parameters in production)
    # For now, we'll just scale by a fixed factor
    features[:, :6] = features[:, :6] / 10.0  # Accelerometer and gyroscope data
    features[:, 6] = features[:, 6] / 100.0   # Speed data
    
    # Reshape for LSTM input (samples, timesteps, features)
    # For real-time prediction, we might use a sliding window approach
    return features.reshape(1, len(features), -1)

def load_model(model_path="accident_detection_model.h5"):
    """
    Load a trained model from disk
    
    Args:
        model_path: Path to the saved model file
        
    Returns:
        Loaded Keras model
    """
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def save_model(model, model_path="accident_detection_model.h5"):
    """
    Save a trained model to disk
    
    Args:
        model: Keras model to save
        model_path: Path to save the model file
    """
    try:
        model.save(model_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"Error saving model: {e}")