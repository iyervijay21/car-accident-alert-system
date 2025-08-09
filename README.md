# Car Accident Alert System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![React](https://img.shields.io/badge/react-18%2B-blue)
![FastAPI](https://img.shields.io/badge/fastapi-latest-brightgreen)

A full-stack, AI-powered car accident detection and alert system with real-time monitoring, machine learning inference, and emergency notification capabilities. The system uses ESP32 microcontrollers with MPU6050 sensors for edge-based accident detection and a web-based dashboard for monitoring and management.

## 🚀 Features

### Core System Features
- **Real-time Accident Detection**: Uses ML models to analyze sensor data and detect accidents
- **Emergency Alerts**: Automatically sends SMS and email alerts to emergency contacts
- **User Management**: Secure authentication and profile management
- **Contact Management**: Maintain a list of emergency contacts
- **Data Visualization**: Real-time dashboard with sensor data and accident alerts
- **Historical Reports**: Analytics and reporting on past accidents
- **Containerized Deployment**: Docker-based deployment for easy scaling

### ESP32 Edge Detection Features
- **ML-Based Detection**: Replaces simple threshold-based detection with intelligent pattern recognition
- **Real-time Performance**: 50Hz sensor sampling with <50ms inference time
- **Manual Override**: 15-second cancellation period for false alarms
- **SMS Notifications**: Automatic emergency messages with GPS location
- **Memory Efficient**: Optimized for ESP32's limited resources (<500KB memory usage)
- **Modular Design**: Clean separation of concerns for maintainability

## 🏗️ Architecture

### System Components
1. **ESP32 Edge Devices**: Local accident detection using ML and sensor fusion
2. **Backend API**: Central data processing, user management, and alert coordination
3. **Frontend Dashboard**: Web interface for monitoring, reporting, and configuration
4. **Database**: PostgreSQL for persistent data storage
5. **Notification Services**: Twilio for SMS and SendGrid for email alerts

### Tech Stack

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **ML**: TensorFlow/Keras for accident detection
- **Authentication**: JWT tokens
- **Notifications**: Twilio (SMS) and SendGrid (Email)

#### Frontend
- **Framework**: React with TypeScript
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **State Management**: React Context API
- **Routing**: React Router

#### Edge Computing (ESP32)
- **Microcontroller**: ESP32 with MicroPython
- **Sensors**: MPU6050 (Accelerometer/Gyroscope), SIM700C (GPS/GSM)
- **ML Framework**: TensorFlow Lite for Microcontrollers
- **Communication**: UART/I2C protocols

#### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Ready for cloud deployment (AWS, GCP, Azure)

## 📁 Project Structure

```
.
├── backend/                    # FastAPI backend server
│   ├── api/                    # API routers and endpoints
│   ├── core/                   # Core configuration and security
│   ├── models/                 # Database models
│   ├── schemas/                # Pydantic schemas
│   ├── utils/                  # Utility functions
│   ├── ml/                     # Machine learning components
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Unit and integration tests
│   ├── requirements.txt        # Python dependencies
│   └── ...
├── frontend/                   # React frontend dashboard
│   ├── public/                 # Static assets
│   ├── src/                    # Source code
│   ├── Dockerfile              # Frontend Docker configuration
│   └── ...
├── esp32_accident_detector/    # ESP32 edge detection system
│   ├── ml/                     # ML training and inference
│   ├── sensors/                # Sensor interfaces
│   ├── alert/                  # Alert system
│   ├── accident_model.tflite   # TensorFlow Lite model
│   ├── main_esp32.py           # ESP32 main application
│   └── ...
├── docker-compose.yml          # Docker Compose configuration
└── ...
```

## 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd car-accident-alert-system
   ```

2. **Set up environment variables**:
   ```bash
   # Copy and update the environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Start the application**:
   ```bash
   docker-compose up -d
   ```

4. **Access the applications**:
   - Frontend Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### ESP32 Component Tests
```bash
cd esp32_accident_detector
python -m pytest tests/ -v
```

## 🛠️ Development

### Backend Development

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Development

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### ESP32 Development

1. Install dependencies:
   ```bash
   pip install -r esp32_accident_detector/requirements.txt
   ```

2. Generate training data:
   ```bash
   python esp32_accident_detector/ml/generate_data.py --sequences 1000
   ```

3. Train the model:
   ```bash
   python esp32_accident_detector/ml/train.py
   ```

## 🗄️ Database Migrations

To create and run database migrations:

```bash
cd backend
alembic revision --autogenerate -m "Migration message"
alembic upgrade head
```

## 🤖 ML Model Training

To train the accident detection model:

```bash
cd backend
python ml/train.py --data sample_training_data.csv
```

For ESP32 edge models:
```bash
cd esp32_accident_detector
python ml/train.py
```

## ☁️ Deployment

The application is containerized with Docker and can be deployed to any cloud platform that supports Docker containers.

### Using Docker Compose (Local Deployment)
```bash
docker-compose up -d
```

### Individual Container Deployment
```bash
# Build and run backend
cd backend
docker build -t car-accident-backend .
docker run -p 8000:8000 car-accident-backend

# Build and run frontend
cd frontend
docker build -t car-accident-frontend .
docker run -p 3000:3000 car-accident-frontend
```

### ESP32 Deployment

1. Flash MicroPython to ESP32 board
2. Upload all files in `esp32_accident_detector` directory to ESP32
3. Connect hardware components:
   - MPU6050: I2C (GPIO 21/22)
   - SIM700C: UART (GPIO 16/17)
   - Button: GPIO 18
   - LED: GPIO 2
4. Run on ESP32:
   ```python
   import main_esp32
   main_esp32.run()
   ```

## 🔧 Hardware Setup

### ESP32 Connections
1. **MPU6050 Connection**:
   - VCC → ESP32 3.3V
   - GND → ESP32 GND
   - SCL → ESP32 GPIO 22
   - SDA → ESP32 GPIO 21

2. **SIM700C Connection**:
   - VCC → External power (3.7V-4.2V)
   - GND → Common ground
   - TXD → ESP32 GPIO 17
   - RXD → ESP32 GPIO 16

3. **User Interface**:
   - Button: One side → ESP32 GPIO 18, Other side → GND
   - LED: Anode → ESP32 GPIO 2 (with 220Ω resistor), Cathode → GND

## 🔄 CI/CD

The project includes GitHub Actions workflows for:
- Running tests on pull requests
- Building and deploying Docker images
- Retraining ML models when triggered

## 🔐 Environment Variables

See `backend/.env.example` and `frontend/.env.example` for required environment variables.

## 📊 Performance Characteristics

### ESP32 Edge System
- **Model Size**: 37KB (TFLite format)
- **Inference Time**: <50ms on ESP32
- **Memory Usage**: <500KB
- **Sensor Sampling**: 50Hz
- **Detection Window**: 1 second
- **False Positive Rate**: <2% (based on validation)
- **Alert Delay**: 15 seconds (user override)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special recognition for the open-source libraries and tools that made this project possible