import joblib


model = joblib.load(
    "ml/hive_health_model.pkl"
)


# -----------------------------------------
# NORMAL HIVE
# -----------------------------------------

normal_hive = [[
    34.2,   # temperature
    62.4,   # humidity
    38.7,   # weight
    71.3    # acoustic
]]


prediction = model.predict(normal_hive)[0]
probability = model.predict_proba(normal_hive)[0][1]


print("NORMAL HIVE")
print("Prediction:", prediction)
print(
    f"Stress probability: {probability:.2%}"
)


# -----------------------------------------
# STRESS-RISK HIVE
# -----------------------------------------

stress_hive = [[
    39.0,
    84.0,
    30.5,
    94.0
]]


prediction = model.predict(stress_hive)[0]
probability = model.predict_proba(stress_hive)[0][1]


print()
print("STRESS-RISK HIVE")
print("Prediction:", prediction)
print(
    f"Stress probability: {probability:.2%}"
)