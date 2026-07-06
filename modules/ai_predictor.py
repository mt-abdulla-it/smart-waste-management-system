import numpy as np
from sklearn.linear_model import LinearRegression

# Train a simple model on module load with simulated historical data
# Features: [current_fill_level, time_of_day (0-23)]
# Target: hours_to_full
X_train = np.array([
    [10, 8], [20, 9], [50, 12], [80, 15], [90, 17],
    [5, 20], [15, 22], [40, 2], [60, 5], [75, 7]
])
# Simulated hours until bin reaches 100%
y_train = np.array([24.0, 20.0, 12.0, 5.0, 2.0, 30.0, 26.0, 18.0, 10.0, 6.0])

model = LinearRegression()
model.fit(X_train, y_train)

def predict_overflow_time(fill_level):
    """
    AI prediction model using Scikit-Learn Linear Regression.
    Predicts based on current fill level and a mocked time of day (12 PM default).
    Returns estimated hours until the bin reaches 100%.
    """
    if fill_level >= 100:
        return 0.0
        
    # Assume time of day is 12 (noon) for this basic prediction
    features = np.array([[fill_level, 12]])
    prediction = model.predict(features)[0]
    
    # Ensure prediction is logical (not negative, not excessively high)
    hours_to_full = max(0.1, min(prediction, 72.0))
    return round(hours_to_full, 1)
