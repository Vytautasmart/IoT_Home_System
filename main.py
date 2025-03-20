import time
import threading
import serial
from data_processing import read_serial
import visualization  # Import the Dash-based visualization script

# Serial connection settings
SERIAL_PORT = 'COM5'  # Change this to match your Arduino's port
BAUD_RATE = 115200
TIMEOUT = 1

# Initialize Serial Port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)


def serial_thread():
    """Thread to read serial data from Arduino"""
    read_serial(ser)


def main():
    print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
    
    # Give Arduino time to reset
    time.sleep(2)

    # Start Serial Thread (Reads data continuously)
    thread = threading.Thread(target=serial_thread, daemon=True)
    thread.start()

    # Start Dash Visualization (Runs in separate thread inside visualization.py)
    print("Starting IoT Sensor Dashboard...")
    
    # The Dash server runs automatically in the background from visualization.py
    while True:
        time.sleep(1)  # Keeps the main thread alive


if __name__ == "__main__":
    main()
