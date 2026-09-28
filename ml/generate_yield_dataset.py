import random
import pandas as pd


random.seed(42)

rows = []


for _ in range(1000):

    temperature = random.uniform(28, 38)
    humidity = random.uniform(45, 85)

    hive_weight = random.uniform(25, 50)

    flowering_score = random.uniform(0, 1)

    health_score = random.uniform(40, 100)

    # Prototype synthetic relationship
    yield_kg = (
        (hive_weight * 0.20)
        + (flowering_score * 4.0)
        + (health_score * 0.04)
        - (abs(33 - temperature) * 0.10)
        - (abs(65 - humidity) * 0.03)
        + random.uniform(-0.5, 0.5)
    )

    yield_kg = max(0, yield_kg)

    rows.append({
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "hive_weight": round(hive_weight, 2),
        "flowering_score": round(flowering_score, 2),
        "health_score": round(health_score, 2),
        "yield_kg": round(yield_kg, 2)
    })


df = pd.DataFrame(rows)

df.to_csv(
    "ml/honey_yield_dataset.csv",
    index=False
)

print("Honey yield dataset created!")
print(f"Total samples: {len(df)}")
print(df.head())