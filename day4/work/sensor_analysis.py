import json

# Sensor data from fetch_my_data
data = {
    "lab": "AAASEC2 Research Lab",
    "sensors": [
        {"id": "S01", "location": "Room A", "temperature_c": 22.4, "humidity_pct": 45.2},
        {"id": "S02", "location": "Room B", "temperature_c": 24.1, "humidity_pct": 51.7},
        {"id": "S03", "location": "Server Room", "temperature_c": 18.9, "humidity_pct": 38.5},
        {"id": "S04", "location": "Room D", "temperature_c": 23.6, "humidity_pct": 47.0}
    ]
}

sensors = data["sensors"]

# Compute average temperature and humidity
total_temp = sum(s["temperature_c"] for s in sensors)
total_humidity = sum(s["humidity_pct"] for s in sensors)
count = len(sensors)
avg_temp = total_temp / count
avg_humidity = total_humidity / count

# Find hottest and coldest rooms
hottest = max(sensors, key=lambda s: s["temperature_c"])
coldest = min(sensors, key=lambda s: s["temperature_c"])

# Print results
print(f"Average temperature: {avg_temp:.2f}°C")
print(f"Average humidity: {avg_humidity:.2f}%")
print(f"Hottest room: {hottest['location']} ({hottest['temperature_c']}°C)")
print(f"Coldest room: {coldest['location']} ({coldest['temperature_c']}°C)")