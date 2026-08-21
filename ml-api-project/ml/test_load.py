# The script loaded the binary file from disk directly into memory—without needing to retrain the model or download the original dataset

import joblib
import pandas as pd

def test_reloaded_model():
    model_path = "ml/saved_model/model.joblib"
    print(f"1. Loading saved model from {model_path}...")
    pipeline = joblib.load(model_path)

    # Simulated sample input payload (1 block group)
    sample_input = pd.DataFrame([{
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        "AveRooms": 6.9841,
        "AveBedrms": 1.0238,
        "Population": 322.0,
        "AveOccup": 2.5555,
        "Latitude": 37.88,
        "Longitude": -122.23
    }])

    print("2. Running inference on sample input...")
    predicted_value = pipeline.predict(sample_input)[0]

    # Converting target scale ($100,000s) to actual USD value
    actual_usd = predicted_value * 100000

    print(f" SUCCESS! Predicted House Price: ${actual_usd:,.2f}")

if __name__ == "__main__":
    test_reloaded_model()
