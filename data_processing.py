from collections import deque

# Threshold Values
lightThreshold = 200     # Light level threshold for darkness
distanceThreshold = 200  # Distance threshold for occupancy (in cm)
tempThreshold = 20       # Temperature threshold (°C) for LED indicator

# Create a deque to store recent values
MAX_POINTS = 50
light_levels = deque(maxlen=MAX_POINTS)
distances = deque(maxlen=MAX_POINTS)
temperatures = deque(maxlen=MAX_POINTS)
security_mode = False


def read_serial(ser):
    global security_mode  # Needed to modify the variable inside the thread
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            try:
                light, distance, temperature = map(float, data.split(','))
                light_levels.append(light)
                distances.append(distance)
                temperatures.append(temperature)
            except ValueError:
                continue  # Skip malformed data
