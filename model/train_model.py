"""
True Sales Forecasting Model - Forecastify
Trains a simple Linear Regression model on historical monthly sales data.
Run once: python model/train_model.py
Output:   model/sales_model.pkl
"""

import os
import pickle
import numpy as np

# -----------------------------------------------------------------------
# Historical Monthly Data (Aggregated from database_seed_data.sql)
# -----------------------------------------------------------------------
HISTORICAL_DATA = [
    {"month": "2026-06", "month_index": 1, "revenue": 10047234.00, "status": "Complete"},
    {"month": "2026-07", "month_index": 2, "revenue": 16880298.00, "status": "Complete"},
    {"month": "2026-08", "month_index": 3, "revenue": 16308195.20, "status": "Complete"},
    {"month": "2026-09", "month_index": 4, "revenue":  2138696.00, "status": "Incomplete / Current Month"} 
]

def build_dataset():
    """Extract feature X (month_index) and target y (revenue)."""
    X, y = [], []
    for row in HISTORICAL_DATA:
        X.append([row["month_index"]])
        y.append(row["revenue"])
    return np.array(X, dtype=float), np.array(y, dtype=float)

def train():
    """Train the time-series model and save it."""
    from sklearn.linear_model import LinearRegression

    X, y = build_dataset()

    # Filter for complete months only
    X_train = []
    y_train = []
    for i, row in enumerate(HISTORICAL_DATA):
        if row["status"] == "Complete":
            X_train.append(X[i])
            y_train.append(y[i])

    # Linear Regression is appropriate for small dataset trend extraction
    model = LinearRegression()
    model.fit(X_train, y_train)

    print("--- Time-Series Sales Forecasting ---")
    print("  Train samples (Months) :", len(X_train))
    print("  Model                  : Linear Regression (Trend)")
    print()
    print("  Historical Data:")
    for row in HISTORICAL_DATA:
        print(f"    {row['month']}: Rs {row['revenue']:>12,.2f} ({row['status']})")

    # Save everything needed for inference
    bundle = {
        "model": model,
        "historical_data": HISTORICAL_DATA,
        "metrics": {
            "note": "Dataset is extremely limited (3 completed months). Forecast uncertainty is high."
        }
    }

    os.makedirs("model", exist_ok=True)
    model_path = os.path.join("model", "sales_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(bundle, f)
    
    print()
    print("  Saved :", model_path)
    return bundle

if __name__ == "__main__":
    train()
