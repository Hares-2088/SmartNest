# Smart Nest: IoT Home Automation System

A powerful and intuitive 🏠 **IoT Home Automation Platform** designed to simplify your smart living experience. With **Smart Nest**, you can:

- 🌡️ **Monitor** your home's temperature and humidity in real-time.
- 💡 **Control** LED indicators for visual feedback with the touch of a button or via automated commands.
- 🚀 **Integrate seamlessly** with MQTT for instant communication and real-time updates.
- 🖥️ **Adapt effortlessly** between development (mocked sensors) and production (real hardware) environments.
- 📊 **Visualize energy usage** with daily, weekly, and monthly stats presented in an intuitive dashboard.

Whether developing on a local Windows machine, deploying to cloud platforms like Vercel, or using real hardware on Raspberry Pi, Smart Nest ensures a flexible and robust solution to meet your home automation needs.

---

## 📊 Stats Page

![Stats Page](https://github.com/user-attachments/assets/f70b1d28-a57c-4242-b799-02339b2df242)

---

## 🏠 Dashboard

![Dashboard](https://github.com/user-attachments/assets/01341f8d-8269-415e-9cc6-cf0c6f4d3efb)

---

## 📈 Plot Visualization

![Plot Visualization](https://github.com/user-attachments/assets/28ed2de9-e4a4-4ef9-8de7-c85a31a234ff)


---

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Endpoints](#endpoints)
7. [Mocking vs Real Hardware](#mocking-vs-real-hardware)
8. [Future Enhancements](#future-enhancements)
10. [License](#license)

---

## Overview

Smart Nest is a smart home IoT solution designed to enable efficient monitoring and control of home environments. The application integrates with real hardware like DHT sensors and LEDs for physical feedback while supporting a mocked environment for testing and development on platforms like Windows or Vercel.

---

## Features

- 🌡️ **Sensor Monitoring**: Real-time temperature and humidity data collection.
- 💡 **LED Control**: Toggle LED states (ON/OFF) through MQTT messages.
- 📊 **Data Visualization**: Daily, weekly, and monthly energy usage stats displayed in an intuitive dashboard.
- 🖥️ **Platform Independence**: Supports mocking for development environments (e.g., Windows or Vercel) and real hardware on Raspberry Pi.
- 🔐 **User Authentication**: Secure login/logout system with hashed passwords.
- 🔗 **API Integration**: RESTful APIs for sensor data and LED control.
- 🚀 **MQTT Communication**: Real-time updates and control using MQTT protocol.

---

## Technologies Used

- 🖥️ **Backend**: Flask, Flask-Login
- 🗄️ **Database**: SQLite
- 📡 **IoT Protocol**: MQTT (via `paho-mqtt`)
- 🛠️ **Hardware**: DHT22 Sensor, Raspberry Pi GPIO, LED
- 🎭 **Mocking**: Custom mock classes for sensors and LED
- 🌐 **Frontend**: Flask templates (HTML, CSS)
- 🔧 **Other Tools**: Adafruit DHT library, Werkzeug, Flask-CORS

---

## Installation

### Prerequisites

- Python 3.10+
- Pip package manager
- Hardware setup: DHT22/DHT11 sensor, Raspberry Pi (optional)
- MQTT broker (e.g., Mosquitto)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/smart-nest.git
   cd smart-nest
   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   
3. Set up environment variables: Create a .env file and add:
   ```bash
    SECRET_KEY=your_secret_key
    DB_FILE=smartnest.db
    DATA_DIR=data
    BROKER=localhost
    PORT=1883
   
4. Initialize the database:
   ```bash
   python app.py

## Usage

### Access the Application

1. Navigate to `http://localhost:5000` in your browser.
2. Use the default admin credentials:
   - **Username**: `admin`
   - **Password**: `password123`

### Functionalities

- View live sensor data on the dashboard.
- Control the LED from the browser.
- Monitor energy usage statistics.
- Access RESTful APIs for programmatic control.

---

## Endpoints

### API Endpoints

| Method | Endpoint           | Description                           |
|--------|--------------------|---------------------------------------|
| GET    | `/api/sensor`      | Fetch live temperature and humidity. |
| GET    | `/api/led/<state>` | Control the LED (state = `on`/`off`).|

### Web Routes

| Method | Route        | Description                 |
|--------|--------------|-----------------------------|
| GET    | `/`          | Redirect to the dashboard. |
| GET    | `/login`     | User login page.           |
| GET    | `/logout`    | Log out current user.      |
| GET    | `/dashboard` | View the main dashboard.   |
| GET    | `/stats`     | View energy usage stats.   |
| GET    | `/plots`     | View historical usage data.|

---

## Mocking vs Real Hardware

The application intelligently switches between mocked sensors and real hardware based on the platform:

- **Mocking**: Used for Windows development or Vercel deployment.
- **Real Sensors**: Automatically enabled on Raspberry Pi with DHT22/DHT11 sensors and GPIO LEDs.

### Mocked Components

- **Temperature/Humidity Sensor**: Generates random fluctuations.
- **LED**: Logs state changes (ON/OFF) to the console.

### Real Components

- **DHT22/DHT11**: Uses the Adafruit DHT library.
- **LED**: Controlled via GPIO pins.

---

## Future Enhancements

- Integration with cloud platforms (e.g., AWS IoT, Google Cloud IoT).
- Support for additional sensors (e.g., motion detection, light intensity).
- Mobile-friendly design for better UX.
- Historical data export to CSV.
- Enhanced authentication with OAuth support.

---

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

---

## Acknowledgments

- **Adafruit**: For the DHT sensor library and documentation.
- **Paho MQTT**: For the MQTT client implementation.
- **Flask**: For the lightweight and flexible web framework.
- **ChatGPT**: couldn't have understood all of the above without him.

---

## Contact

If you have any questions, suggestions, or feedback, feel free to reach out:

- **Email**: [adembessam@gmail.com](mailto:adembessam@gmail.com)






