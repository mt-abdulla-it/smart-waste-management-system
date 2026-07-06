import random

def predict_overflow_time(fill_level):
    """
    Mock AI prediction model.
    In a real scenario, this would use Scikit-Learn (Linear Regression/Random Forest)
    based on historical fill rates, day of the week, and weather data.
    
    Returns estimated hours until the bin reaches 100%.
    """
    if fill_level >= 100:
        return 0
        
    remaining_capacity = 100 - fill_level
    
    # Mock varying fill rates based on random generation (e.g., 2% to 10% per hour)
    fill_rate_per_hour = random.uniform(2.0, 10.0)
    
    hours_to_full = remaining_capacity / fill_rate_per_hour
    
    return round(hours_to_full, 1)
