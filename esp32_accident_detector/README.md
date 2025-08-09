# ESP32 Car Accident Detection System

A machine learning-based car accident detection system using ESP32 with MPU6050 and SIM7000C modules.

## Features

- **ML-based Accident Detection**: Uses LSTM neural network to analyze sensor data
- **Real-time Sensor Fusion**: Combines accelerometer, gyroscope, and GPS data
- **Emergency Alerts**: Automatically sends SMS with location via SIM7000C
- **Manual Override**: 15-second cancellation period with physical button
- **Low Power Optimization**: Designed for battery-powered operation
- **Modular Architecture**: Clean, well-commented code for easy maintenance

## Hardware Requirements

- ESP32 development board (ESP32-WROOM-32 recommended)
- MPU6050 accelerometer/gyroscope module
- SIM700C GSM/GPS module
- Push button for alert override
- LED for status indication
- Jumper wires and breadboard

## Wiring Diagram

```
MPU6050:
- VCC  → ESP32 3.3V
- GND  → ESP32 GND
- SCL  → ESP32 GPIO 22 (SCL)
- SDA  → ESP32 GPIO 21 (SDA)

SIM7000C:
- VCC  → External power supply (3.7V-4.2V)
- GND  → Common ground
- TXD  → ESP32 GPIO 17 (RXD)
- RXD  → ESP32 GPIO 16 (TXD)

Button:
- One side → ESP32 GPIO 18
- Other side → ESP32 GND

LED:
- Anode → ESP32 GPIO 2 (with 220Ω resistor)
- Cathode → ESP32 GND
```

## Software Architecture

The system is organized into modular components:

1. **Sensors**: MPU6050 interface and sensor fusion
2. **ML**: Model training and inference
3. **Alert**: SIM7000C communication and SMS handling
4. **Main**: System controller and coordination

## Installation (PC Testing)

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Generate sample training data:
```bash
python ml/train.py --generate_sample
```

3. Train the accident detection model:
```bash
python ml/train.py --data sample_data.csv --output models/accident_model.h5
```

## Model Training

The system uses a lightweight LSTM model optimized for embedded deployment:

```bash
python ml/train.py --data training_data.csv --sequence_length 50 --epochs 50
```

The training script automatically converts the model to TensorFlow Lite format for efficient inference on ESP32.

## Configuration

Edit `config.py` to adjust system parameters:
- `CONFIDENCE_THRESHOLD`: Minimum confidence for accident detection (0.0-1.0)
- `ALERT_DELAY`: Seconds to wait before sending alert (allows override)
- `PHONE_NUMBER`: Emergency contact number
- `SAMPLING_RATE`: Sensor data sampling rate in Hz

## ESP32 Deployment

For ESP32 deployment, the system uses MicroPython. The main differences from the PC version are:

1. Hardware-specific libraries (machine module instead of RPi.GPIO)
2. Direct I2C communication with MPU6050
3. UART communication with SIM7000C
4. Optimized memory usage

## Testing

Run unit tests:
```bash
python -m unittest tests/test_preprocessing.py
```

## Power Management

For battery-powered operation:
- Use deep sleep modes during low activity periods
- Implement dynamic frequency scaling
- Consider using external power management ICs

## Troubleshooting

Common issues:
1. I2C communication errors: Check wiring and pull-up resistors
2. Serial communication issues: Verify SIM7000C connections and baud rate
3. Model loading failures: Ensure model file exists and is compatible
4. False positives: Adjust confidence threshold or retrain with more data

## Future Improvements

- Add OTA firmware updates
- Implement edge caching for offline operation
- Add Bluetooth configuration interface
- Include airbag deployment interface
- Add cloud connectivity for data backup