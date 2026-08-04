#import
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import json

# Load the cleaned, labeled dataset saved by load_data.py
df = pd.read_csv("cleaned_data.csv")

# Features: the sensor/weather readings the model learns from.
# Note: PM2.5 is deliberately left out. Since risk_level was calculated
# directly FROM PM2.5, including it would let the model just look up
# the answer instead of actually learning the relationship between
# other conditions (pollutants, weather) and risk.
feature_columns = ["PM10", "SO2", "NO2", "CO", "O3",
                    "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
X = df[feature_columns]

# Target: the category we want the model to predict
y = df["risk_level"]

# XGBoost needs numbers, not text labels, so convert
# "Good"/"Moderate"/"Unhealthy"/"Hazardous" into 0/1/2/3
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split the data: 80% to train on, 20% held back to test on
# afterward, so we can check accuracy on data the model never saw
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Train the model
model = xgb.XGBClassifier(eval_metric="mlogloss")
model.fit(X_train, y_train)

# Check how accurate it is on the unseen test data
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy on test data: {accuracy:.2%}")

print("\nDetailed performance per category:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Save the trained model to a file
model.save_model("aqi_model.json")
print("\nSaved aqi_model.json")

# Save the label order too, so inference can later convert the model's
# numeric answer (e.g. 3) back into a readable word (e.g. "Hazardous")
label_mapping = {i: label for i, label in enumerate(label_encoder.classes_)}
with open("label_mapping.json", "w") as f:
    json.dump(label_mapping, f)
print("Saved label_mapping.json")