# COE892 Project Readme

## Project Details
This project entails the creation of a satellite network monitoring system and dashboard.  It keeps track of the following: the number of clients within a given service area, peak usage times of the system, and key logs of satellites in orbit. The backend portion is a combination of FastAPI application utilizing websockets for real-time data, RabbitMQ to handle logs, MongoDB for storage.

---

## Setup Instructions

### 1. Create a Virtual Environment
To isolate dependencies, create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows**:
    ```bash
    .\venv\Scripts\activate
    ```
- **macOS/Linux**:
    ```bash
    source venv/bin/activate
    ```

### 2. Install Requirements
Install the required dependencies from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## Run Instructions

### 1. Start the FastAPI Application
Run the FastAPI application using the following command:
```bash
fastapi dev api/main.py
```
This will start the server, and you can access the API documentation at `http://127.0.0.1:8000/docs`.

### 2. Boot the RabbitMQ Consumer
Run the consumer script to handle logging tasks:
```bash
python logging/log_consumer.py
```

### 3. Run the Network Script
Execute the `network.py` script to start up the satellite network.
```bash
python network.py
```

---

## Notes
- Ensure all required environment variables are set before running the application, provided in an email and in a txt file in D2L submission.
