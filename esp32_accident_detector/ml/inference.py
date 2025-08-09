import numpy as np
import tensorflow as tf
from typing import Optional, Tuple
import os
from config import Config

class AccidentInference:
    """
    ML inference module optimized for ESP32 deployment
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.config = Config()
        self.model_path = model_path or self.config.MODEL_PATH
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.model_loaded = False
        
        # Try to load model
        self.load_model()
    
    def load_model(self) -> bool:
        """
        Load TensorFlow Lite model
        Returns: True if model loaded successfully
        """
        try:
            # Check if model file exists
            if not os.path.exists(self.model_path):
                print(f"Model file not found: {self.model_path}")
                return False
            
            # Load TFLite model
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            print(f"Model loaded successfully from {self.model_path}")
            print(f"Input shape: {self.input_details[0]['shape']}")
            print(f"Output shape: {self.output_details[0]['shape']}")
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.interpreter = None
            self.model_loaded = False
            return False
    
    def predict(self, sensor_data: np.ndarray) -> Tuple[bool, float]:
        """
        Predict if an accident occurred based on sensor data
        sensor_data: numpy array of shape (1, timesteps, features)
        Returns: (is_accident, confidence)
        """
        if not self.model_loaded:
            print("Model not loaded")
            return False, 0.0
        
        if sensor_data is None:
            return False, 0.0
            
        try:
            # Ensure data is float32
            if sensor_data.dtype != np.float32:
                sensor_data = sensor_data.astype(np.float32)
            
            # Set input tensor
            self.interpreter.set_tensor(self.input_details[0]['index'], sensor_data)
            
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
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model
        """
        if not self.model_loaded:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "input_shape": self.input_details[0]['shape'].tolist(),
            "output_shape": self.output_details[0]['shape'].tolist(),
            "input_type": str(self.input_details[0]['dtype']),
            "output_type": str(self.output_details[0]['dtype']),
            "threshold": self.config.CONFIDENCE_THRESHOLD
        }
    
    def update_threshold(self, new_threshold: float) -> bool:
        """
        Update accident detection threshold
        Returns: True if threshold was updated
        """
        if 0.0 <= new_threshold <= 1.0:
            self.config.CONFIDENCE_THRESHOLD = new_threshold
            print(f"Updated confidence threshold to {new_threshold}")
            return True
        else:
            print("Threshold must be between 0.0 and 1.0")
            return False

# Fallback implementation for systems without TensorFlow Lite
class FallbackInference:
    """
    Fallback inference implementation for systems without TensorFlow Lite
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.config = Config()
        self.model_path = model_path or self.config.MODEL_PATH
        print("TensorFlow Lite not available, using fallback implementation")
        print("WARNING: This implementation always returns False for accident detection")
    
    def load_model(self) -> bool:
        """Fallback model loading"""
        print("Fallback implementation: No model to load")
        return True
    
    def predict(self, sensor_data: np.ndarray) -> Tuple[bool, float]:
        """
        Fallback prediction (always returns False)
        """
        return False, 0.0
    
    def get_model_info(self) -> dict:
        """Get model info for fallback"""
        return {
            "loaded": True,
            "fallback": True,
            "message": "Using fallback implementation"
        }
    
    def update_threshold(self, new_threshold: float) -> bool:
        """Update threshold for fallback"""
        if 0.0 <= new_threshold <= 1.0:
            self.config.CONFIDENCE_THRESHOLD = new_threshold
            return True
        return False

# Try to import TensorFlow Lite, fallback if not available
try:
    import tensorflow as tf
    # Test if TFLite is available
    tf.lite.Interpreter
    # Use the real implementation
    AccidentDetector = AccidentInference
except (ImportError, AttributeError):
    # Use fallback implementation
    AccidentDetector = FallbackInference
    print("TensorFlow Lite not available, using fallback implementation")