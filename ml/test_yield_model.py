import joblib


model = joblib.load(
    "ml/honey_yield_model.pkl"
)


# Example hive conditions

temperature = 34.2
humidity = 62.4
hive_weight = 38.7
flowering_score = 0.75
health_score = 92


features = [[
    temperature,
    humidity,
    hive_weight,
    flowering_score,
    health_score
]]


prediction = model.predict(features)[0]


print()
print("🐝 HONEY YIELD PREDICTION")
print("-" * 35)

print(f"Temperature: {temperature} °C")
print(f"Humidity: {humidity} %")
print(f"Hive Weight: {hive_weight} kg")
print(f"Flowering Score: {flowering_score}")
print(f"Health Score: {health_score}")

print()
print(
    f"Predicted Honey Yield: {prediction:.2f} kg"
)