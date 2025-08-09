# Car Accident Detection System

A Raspberry Pi based car accident detection system using MPU6050 sensors, SIM7000C communication module, and machine learning for real-time accident detection.

## Features

- Real-time accelerometer and gyroscope data collection using MPU6050
- GPS location tracking
- ML-based accident detection using LSTM/CNN models
- Emergency SMS alerts with location links via SIM7000C
- 15-second manual override button to cancel false alerts
- Low power optimization for embedded deployment

## Hardware Requirements

- Raspberry Pi (3B+ or newer recommended)
- MPU6050 accelerometer/gyroscope module
- SIM700C GSM/GPS module
- Push button for alert override
- LED for status indication
- Jumper wires and breadboard

## Wiring Diagram

```
MPU6050:
- VCC  → Pi 3.3V
- GND  → Pi GND
- SCL  → Pi GPIO 3 (SCL)
- SDA  → Pi GPIO 2 (SDA)

SIM7000C:
- VCC  → External power supply (3.7V-4.2V)
- GND  → Common ground
- TXD  → Pi GPIO 15 (RXD)
- RXD  → Pi GPIO 14 (TXD)

Button:
- One side → Pi GPIO 18
- Other side → Pi GND

LED:
- Anode → Pi GPIO 24 (with 220Ω resistor)
- Cathode → Pi GND
```

## Installation

1. Install required packages:
```bash
sudo apt update
sudo apt install python3-pip python3-smbus git

# Install Python dependencies
pip3 install -r requirements.txt
```

2. Enable I2C interface:
```bash
sudo raspi-config
# Navigate to Interfacing Options > I2C > Enable
```

3. Clone the repository:
```bash
git clone <repository-url>
cd car_accident_detector
```

## Training the Model

1. Generate sample training data:
```bash
python3 generate_training_data.py --hours 10 --accidents 20 --output training_data.csv
```

2. Train the accident detection model:
```bash
python3 ml/train_model.py --data training_data.csv --model_type lstm --output models/accident_model.h5
```

3. The training script will automatically convert the model to TensorFlow Lite format for embedded deployment.

## Configuration

Edit `config.py` to adjust system parameters:
- `CONFIDENCE_THRESHOLD`: Minimum confidence for accident detection (0.0-1.0)
- `ALERT_DELAY`: Seconds to wait before sending alert (allows override)
- `PHONE_NUMBER`: Emergency contact number
- `SAMPLING_RATE`: Sensor data sampling rate in Hz

## Usage

1. Run the main detection system:
```bash
python3 main.py
```

2. The system will:
   - Initialize all sensors and communication modules
   - Continuously monitor sensor data
   - Run ML inference on sensor data windows
   - Trigger alerts when accidents are detected
   - Allow 15-second override period via button press

## Testing

Run unit tests:
```bash
python3 -m unittest tests/test_preprocessing.py
```

## Model Optimization

The system uses TensorFlow Lite for efficient inference on embedded devices:
- Models are quantized for reduced size and faster execution
- LSTM model is recommended for sequential pattern recognition
- 1D CNN model provides an alternative with different characteristics

## Power Management

For battery-powered operation:
- Use `vcgencmd` to monitor Pi temperature and adjust performance
- Implement sleep modes during low activity periods
- Consider using a Pi UPS for graceful shutdown

## Troubleshooting

Common issues:
1. I2C communication errors: Check wiring and enable I2C interface
2. Serial communication issues: Verify SIM7000C connections and baud rate
3. Model loading failures: Ensure model file exists and is compatible
4. False positives: Adjust confidence threshold or retrain with more data

## Future Improvements

- Integrate camera for visual accident confirmation
- Add cloud connectivity for data backup and remote monitoring
- Implement edge caching for offline operation
- Add voice alerts through speaker
- Include airbag deployment interface