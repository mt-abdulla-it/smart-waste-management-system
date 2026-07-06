import datetime

def process_alerts(bin_id, fill_level, threshold=80):
    """
    Checks if a bin exceeds the threshold and triggers an alert.
    """
    if fill_level >= 95:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_msg = f"[CRITICAL EMERGENCY - {timestamp}] Bin ID {bin_id} is at {fill_level}%! BYPASSING SCHEDULE. IMMEDIATE PICKUP DISPATCHED."
        print(alert_msg)
        return "CRITICAL"
    elif fill_level >= threshold:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_msg = f"[ALERT - {timestamp}] Bin ID {bin_id} has reached {fill_level}% capacity! Urgent collection required."
        print(alert_msg)
        # In a real scenario, integrate with Twilio (SMS) or SMTP (Email) here.
        return "WARNING"
    return "SAFE"

def check_budget_alert(current_total_cost, monthly_budget_limit=120000.0):
    """
    Triggers an alert if the total cost exceeds 85% of the monthly budget limit.
    """
    threshold_cost = monthly_budget_limit * 0.85
    if current_total_cost >= threshold_cost:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        percent_used = (current_total_cost / monthly_budget_limit) * 100
        alert_msg = f"[BUDGET WARNING - {timestamp}] Warning: Budget exceeded 85%! (Currently at {percent_used:.1f}%)"
        print(alert_msg)
        return True
    return False
