import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import joblib


# -----------------------------------------
# LOAD DATASET
# -----------------------------------------

df = pd.read_csv(
    "ml/hive_health_dataset.csv"
)


# -----------------------------------------
# FEATURES
# -----------------------------------------

X = df[
    [
        "temperature",
        "humidity",
        "hive_weight",
        "acoustic_level"
    ]
]


# -----------------------------------------
# TARGET
# -----------------------------------------

y = df["stress_risk"]


# -----------------------------------------
# TRAIN / TEST SPLIT
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# -----------------------------------------
# MODEL
# -----------------------------------------

model = RandomForestClassifier(
    n_estimators=100,
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

accuracy = accuracy_score(
    y_test,
    predictions
)


print("Model training completed.")
print(f"Test accuracy on synthetic dataset: {accuracy:.2%}")


# -----------------------------------------
# SAVE MODEL
# -----------------------------------------

joblib.dump(
    model,
    "ml/hive_health_model.pkl"
)


print("Model saved successfully.")