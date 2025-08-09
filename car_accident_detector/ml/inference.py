import numpy as np
import tensorflow as tf
from typing import Optional, Tuple
from ..config import Config

class AccidentDetector:
    """
    ML-based accident detection using TensorFlow Lite model
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.config = Config()
        self.model_path = model_path or self.config.MODEL_PATH
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.load_model()
    
    def load_model(self):
        """
        Load TensorFlow Lite model
        """
        try:
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            print(f"Model loaded successfully from {self.model_path}")
            print(f"Input shape: {self.input_details[0]['shape']}")
            print(f"Output shape: {self.output_details[0]['shape']}")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.interpreter = None
    
    def predict(self, sensor_data: np.ndarray) -> Tuple[bool, float]:
        """
        Predict if an accident occurred based on sensor data
        sensor_data: numpy array of shape (1, timesteps, features)
        Returns: (is_accident, confidence)
        """
        if self.interpreter is None:
            print("Model not loaded")
            return False, 0.0
        
        if sensor_data is None:
            return False, 0.0
            
        try:
            # Set input tensor
            self.interpreter.set_tensor(self.input_details[0]['index'], sensor_data.astype(np.float32))
            
            # Run inference
            self.interpreter.invoke()
            
            # Get output
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            confidence = float(output_data[0][0])
            is_accident = confidence > self.config.CONFIDENCE_THRESHOLD
            
            return is_accident, confidence
        except Exception as e:
            print(f"Error during prediction: {e}")
            return False, 0.0
    
    def update_threshold(self, new_threshold: float):
        """
        Update accident detection threshold
        """
        self.config.CONFIDENCE_THRESHOLD = new_threshold
        print(f"Updated confidence threshold to {new_threshold}")