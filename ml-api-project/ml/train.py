import os
import joblib
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

def train_and_save_model():
    print("1. Loading California Housing Dataset...")
    data = fetch_california_housing(as_frame=True)
    X = data.data
    y = data.target  # Median house value in $100k units

    # 2. Train / Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("2. Building ML Pipeline (Scaler + Random Forest)...")
    # Packaging scaling + model into one unified pipeline solves feature mismatch errors
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    print("3. Training Model...")
    pipeline.fit(X_train, y_train)

    print("4. Evaluating Model...")
    predictions = pipeline.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"   --> Mean Squared Error (MSE): {mse:.4f}")
    print(f"   --> R^2 Score: {r2:.4f}")

    # 5. Save the pipeline object to disk
    output_dir = "ml/saved_model"
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "model.joblib")
    
    joblib.dump(pipeline, model_path)
    print(f"5. Model successfully saved to: {model_path}")

if __name__ == "__main__":
    train_and_save_model()