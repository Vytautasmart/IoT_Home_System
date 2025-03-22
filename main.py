import time
import threading
import serial
from data_processing import read_serial
from dashboard import app

# 👇 Update this to match your device's serial port
SERIAL_PORT = 'COM5'        # Example: 'COM5' on Windows, '/dev/ttyUSB0' on Linux/Mac
BAUD_RATE = 115200
TIMEOUT = 1

# 🔌 Connect to Arduino
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    print(f"[INFO] Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
except serial.SerialException as e:
    print(f"[ERROR] Could not open serial port {SERIAL_PORT}. {e}")
    exit(1)

# Thread to handle serial data reading
def serial_thread():
    read_serial(ser)

# Thread to run the Dash dashboard
def dash_thread():
    app.run(debug=False, use_reloader=False)

# Main function to start everything
def main():
    time.sleep(2)  # Allow Arduino to reset

    threading.Thread(target=serial_thread, daemon=True).start()
    threading.Thread(target=dash_thread, daemon=True).start()

    print("[INFO] Dashboard is running. Press Ctrl+C to stop.")

    # Keep the main program alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
