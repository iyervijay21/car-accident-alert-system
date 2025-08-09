# Car Accident Alert System - Frontend

This is the frontend component of the Car Accident Alert System, built with React and TypeScript.

## Features

- User authentication (login/register)
- Dashboard with real-time accident alerts
- Sensor data visualization
- Emergency contact management
- Accident reports and analytics
- Responsive design for mobile and desktop

## Tech Stack

- **Framework**: React with TypeScript
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **State Management**: React Context API
- **Routing**: React Router
- **HTTP Client**: Axios
- **Deployment**: Docker

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Project Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── components/     # Reusable components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── context/        # React context providers
│   ├── hooks/          # Custom hooks
│   ├── utils/          # Utility functions
│   ├── assets/         # Images and other assets
│   ├── theme/          # MUI theme configuration
│   ├── App.tsx         # Main application component
│   └── index.tsx       # Entry point
├── Dockerfile          # Docker configuration
├── nginx.conf          # Nginx configuration
└── package.json        # Project dependencies
```

## Environment Variables

Create a `.env` file with the following variables:

```
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
```

## Development

The frontend development server runs on port 3000 by default. During development, API requests are proxied to the backend server (typically running on port 8000).

## Docker

To build and run the frontend in a Docker container:

```bash
docker build -t car-accident-frontend .
docker run -p 3000:3000 car-accident-frontend
```