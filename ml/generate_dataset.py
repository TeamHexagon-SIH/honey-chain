import random
import pandas as pd


random.seed(42)

rows = []


# -----------------------------------------
# NORMAL HIVE CONDITIONS
# -----------------------------------------

for _ in range(500):

    temperature = random.uniform(32, 36)
    humidity = random.uniform(55, 70)
    hive_weight = random.uniform(35, 42)
    acoustic_level = random.uniform(60, 80)

    rows.append({
        "temperature": temperature,
        "humidity": humidity,
        "hive_weight": hive_weight,
        "acoustic_level": acoustic_level,
        "stress_risk": 0
    })


# -----------------------------------------
# STRESS-RISK CONDITIONS
# -----------------------------------------

for _ in range(500):

    temperature = random.uniform(37.5, 40)
    humidity = random.uniform(75, 90)
    hive_weight = random.uniform(28, 34)
    acoustic_level = random.uniform(85, 100)

    rows.append({
        "temperature": temperature,
        "humidity": humidity,
        "hive_weight": hive_weight,
        "acoustic_level": acoustic_level,
        "stress_risk": 1
    })


df = pd.DataFrame(rows)

df.to_csv(
    "ml/hive_health_dataset.csv",
    index=False
)

print("Dataset created successfully!")
print(f"Total samples: {len(df)}")
print(df.head())