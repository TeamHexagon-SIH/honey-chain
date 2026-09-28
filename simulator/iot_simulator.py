import random
import time
import requests
from datetime import datetime


API_URL = "http://127.0.0.1:8000/api/sensors/readings"

HIVE_ID = 1


def generate_reading(condition="normal"):

    if condition == "normal":

        temperature = random.uniform(32.0, 36.0)
        humidity = random.uniform(55.0, 70.0)
        hive_weight = random.uniform(35.0, 42.0)
        acoustic_level = random.uniform(60.0, 80.0)

    elif condition == "stress":

        temperature = random.uniform(37.5, 40.0)
        humidity = random.uniform(75.0, 90.0)
        hive_weight = random.uniform(28.0, 34.0)
        acoustic_level = random.uniform(85.0, 100.0)

    else:

        temperature = random.uniform(32.0, 36.0)
        humidity = random.uniform(55.0, 70.0)
        hive_weight = random.uniform(35.0, 42.0)
        acoustic_level = random.uniform(60.0, 80.0)

    return {
        "hive_id": HIVE_ID,
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "hive_weight": round(hive_weight, 2),
        "acoustic_level": round(acoustic_level, 2)
    }


def send_reading(reading):

    response = requests.post(
        API_URL,
        params=reading
    )

    if response.status_code == 200:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"Reading sent successfully"
        )

        print(
            f"Temperature: {reading['temperature']} °C | "
            f"Humidity: {reading['humidity']} % | "
            f"Weight: {reading['hive_weight']} kg | "
            f"Acoustic: {reading['acoustic_level']}"
        )

        print("-" * 70)

    else:
        print(
            "Failed to send reading:",
            response.text
        )


while True:

    reading = generate_reading("normal")

    send_reading(reading)

    time.sleep(5)