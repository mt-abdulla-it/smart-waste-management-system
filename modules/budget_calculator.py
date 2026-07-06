def calculate_route_cost(distance_km, fuel_price=350.0, mileage=12.0, driver_rate=500.0, avg_speed=40.0):
    """
    Calculates the financial cost of a route.
    - distance_km: total route distance
    - fuel_price: price per liter (e.g. 350 LKR)
    - mileage: km per liter (e.g. 12 km/l)
    - driver_rate: hourly rate of the driver
    - avg_speed: assumed average speed in km/h for time calculation
    """
    if mileage <= 0:
        mileage = 12.0
        
    fuel_used = distance_km / mileage
    fuel_cost = fuel_used * fuel_price
    
    # Time in hours
    time_hours = distance_km / avg_speed
    driver_cost = time_hours * driver_rate
    
    total_cost = fuel_cost + driver_cost
    
    # Efficiency logic (arbitrary thresholds for demo purposes)
    if distance_km < 10:
        efficiency = "High"
    elif distance_km < 20:
        efficiency = "Medium"
    else:
        efficiency = "Low"
        
    return {
        "fuel_used": round(fuel_used, 2),
        "fuel_cost": round(fuel_cost, 2),
        "driver_cost": round(driver_cost, 2),
        "total_cost": round(total_cost, 2),
        "efficiency": efficiency
    }
