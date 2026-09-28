import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

import joblib


# -----------------------------------------
# LOAD DATA
# -----------------------------------------

df = pd.read_csv(
    "ml/honey_yield_dataset.csv"
)


# -----------------------------------------
# FEATURES
# -----------------------------------------

X = df[
    [
        "temperature",
        "humidity",
        "hive_weight",
        "flowering_score",
        "health_score"
    ]
]


# -----------------------------------------
# TARGET
# -----------------------------------------

y = df["yield_kg"]


# -----------------------------------------
# TRAIN / TEST SPLIT
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# -----------------------------------------
# MODEL
# -----------------------------------------

model = RandomForestRegressor(
    n_estimators=150,
    random_state=42
)


model.fit(
    X_train,
    y_train
)


# -----------------------------------------
# EVALUATION
# -----------------------------------------

predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print("Yield prediction model trained.")
print(f"Mean Absolute Error: {mae:.2f} kg")
print(f"R² Score: {r2:.2f}")


# -----------------------------------------
# SAVE MODEL
# -----------------------------------------

joblib.dump(
    model,
    "ml/honey_yield_model.pkl"
)

print("Yield model saved successfully.")