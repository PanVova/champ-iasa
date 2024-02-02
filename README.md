# Weather Forecast Application

## Overview
This project is a Flask-based web application for providing weather forecasts. It integrates with the OpenMeteo API to fetch and display weather data based on user input. The application is designed to be user-friendly and efficient, offering both current and future weather data.

Here is the quick video showing the project

https://github.com/PanVova/champ-iasa/assets/37262034/ae4b87fb-741c-470e-b3d0-fe2cca1d207e



## Features
- Real-time weather forecasts
- Search functionality for global locations
- Hourly and daily weather data display
- Caching for improved performance
- Robust error handling and input validation

## Technologies Used
- **Flask**: A lightweight WSGI web application framework in Python, used for building the web application.
- **Requests**: Used for making API calls to OpenMeteo.
- **Pandas**: For data manipulation and analysis.
- **NumPy**: Used in data processing and calculations.
- **TensorFlow**: For LSTM model predictions.
- **Joblib**: For loading the pre-trained scaler model.
- **HTML/CSS**: For frontend development.
- **unittest**: Python's built-in library used for writing and running tests.

## Installation
To set up the project locally, follow these steps:
1. Clone the repository: `git clone https://github.com/your-username/your-repository.git`
2. Navigate to the project directory: `cd your-repository`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the Flask application: `python app.py`

To run the project, follow these steps:
1. Create the virtual environment.
```bash
python -m venv .venv
```
2. Activate the virtual environment.
- For Windows, use:
```bash
.venv\Scripts\activate
```
- For macOS/Linux, use:
```bash
source .venv/bin/activate
```
3. Install the dependencies and run the project.
```bash
pip install -r requirements.txt
flask run
```

## Run via Docker Compose
1. docker compose up

## Usage
After running the application, navigate to `http://localhost:5000` in your browser to access the web interface. Enter the location you wish to view the weather forecast for, and the application will display the relevant data.

## Testing
The project includes a test suite to ensure the reliability and performance of the application. To run the tests, execute `python -m unittest test_app.py`.
