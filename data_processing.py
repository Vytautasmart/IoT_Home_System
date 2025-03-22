from collections import deque
import statistics
import csv
from datetime import datetime

MAX_POINTS = 100
temperatures = deque(maxlen=MAX_POINTS)
distances = deque(maxlen=MAX_POINTS)
light_levels = deque(maxlen=MAX_POINTS)
full_log = []

def read_serial(ser):
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                light, distance, temp = map(float, line.split(','))
                light_levels.append(light)
                distances.append(distance)
                temperatures.append(temp)
                full_log.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'light': light,
                    'distance': distance,
                    'temperature': temp
                })
            except ValueError:
                continue

def get_averages():
    if not temperatures:
        return None, None, None
    return (
        sum(light_levels) / len(light_levels),
        sum(distances) / len(distances),
        sum(temperatures) / len(temperatures)
    )

def get_eda_summary():
    return {
        'Temperature': {
            'min': min(temperatures),
            'max': max(temperatures),
            'std_dev': statistics.stdev(temperatures)
        },
        'Distance': {
            'min': min(distances),
            'max': max(distances),
            'std_dev': statistics.stdev(distances)
        },
        'Light': {
            'min': min(light_levels),
            'max': max(light_levels),
            'std_dev': statistics.stdev(light_levels)
        }
    }

def get_trends(window_size=5):
    def trend_arrow(data):
        if len(data) < window_size + 1:
            return "–"
        recent = sum(list(data)[-window_size:]) / window_size
        previous = sum(list(data)[-window_size-1:-1]) / window_size
        return "↑" if recent > previous else "↓" if recent < previous else "→"

    return {
        'Temperature': trend_arrow(temperatures),
        'Distance': trend_arrow(distances),
        'Light': trend_arrow(light_levels)
    }

def export_to_csv(filename="sensor_log.csv"):
    if not full_log:
        return
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['timestamp', 'light', 'distance', 'temperature'])
        writer.writeheader()
        for row in full_log:
            writer.writerow(row)
