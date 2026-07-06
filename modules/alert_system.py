import datetime

def process_alerts(bin_id, fill_level, threshold=80):
    """
    Checks if a bin exceeds the threshold and triggers an alert.
    """
    if fill_level >= 95:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_msg = f"📱 [CMC SMS ALERT - {timestamp}] CRITICAL! Bin {bin_id} at {fill_level}%. Dispatched Emergency Truck to location."
        print(alert_msg)
        return "CRITICAL"
    elif fill_level >= threshold:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_msg = f"✉️ [CMC Email - {timestamp}] Bin {bin_id} reached {fill_level}%. Added to next collection cycle."
        print(alert_msg)
        return "WARNING"
    return "SAFE"

def check_budget_alert(current_total_cost, monthly_budget_limit=5000000.0):
    """
    Triggers an alert if the total cost exceeds 85% of the monthly budget limit.
    """
    threshold_cost = monthly_budget_limit * 0.85
    if current_total_cost >= threshold_cost:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        percent_used = (current_total_cost / monthly_budget_limit) * 100
        alert_msg = f"🚨 [CMC Admin SMS - {timestamp}] Budget alert! {percent_used:.1f}% of LKR {monthly_budget_limit:,.2f} budget consumed."
        print(alert_msg)
        return True
    return False
