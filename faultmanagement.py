import sqlite3
import random
import time
import requests
import json

# Step 1: Set Up the SQLite Database
def setup_database():
    conn = sqlite3.connect('5g_fault_management.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faults
                 (timestamp TEXT, fault_type TEXT, alert_level TEXT, alert_message TEXT)''')
    conn.commit()
    conn.close()

# Step 2: Fault Detection Function
def detect_faults():
    # Simulate 5G metrics
    latency = random.uniform(1.0, 100.0)  # in milliseconds
    signal_strength = random.uniform(-120.0, -40.0)  # in dBm
    packet_loss = random.uniform(0.0, 5.0)  # in percentage

    # Post the metrics to the new_data endpoint
    url = "http://localhost:8000/new_data"  # Corrected URL for new_data endpoint
    data = {
        "latency": latency,
        "signal_strength": signal_strength,
        "packet_loss": packet_loss
    }
    response = requests.post(url, json=data)

    if response.status_code != 200:
        print("Error posting new data:", response.text)

    # Define thresholds for faults
    if latency > 75.0:
        return "High Latency", "red", f"Latency: {latency:.2f} ms"
    elif latency > 50.0:
        return "High Latency", "yellow", f"Latency: {latency:.2f} ms"
    elif signal_strength < -100.0:
        return "Poor Signal Strength", "red", f"Signal Strength: {signal_strength:.2f} dBm"
    elif signal_strength < -85.0:
        return "Poor Signal Strength", "yellow", f"Signal Strength: {signal_strength:.2f} dBm"
    elif packet_loss > 3.5:
        return "High Packet Loss", "red", f"Packet Loss: {packet_loss:.2f}%"
    elif packet_loss > 2.0:
        return "High Packet Loss", "yellow", f"Packet Loss: {packet_loss:.2f}%"
    
    return None, None, None  # No fault detected

# Step 3: Fault Logging Function
def log_fault(fault_type, alert_level, alert_message):
    conn = sqlite3.connect('5g_fault_management.db')
    c = conn.cursor()
    c.execute("INSERT INTO faults (timestamp, fault_type, alert_level, alert_message) VALUES (?, ?, ?, ?)",
              (time.ctime(), fault_type, alert_level, alert_message))
    conn.commit()
    conn.close()

# Global variable to track active alerts
active_alerts = set()

# Step 4: Notify Fault through Print Statements
def notify_fault(fault_type, alert_level, alert_message):
    # Format the alert message
    alert_message = f"ALERT: {fault_type} - {alert_message}"
    print(alert_message)  # Print to console for immediate feedback

    # Determine the field name based on the fault type
    field_name = ""
    if "Latency" in fault_type:
        field_name = "latency"
    elif "Signal Strength" in fault_type:
        field_name = "signal_strength"
    elif "Packet Loss" in fault_type:
        field_name = "packet_loss"

    # Check if this fault type has already been alerted
    alert_identifier = (fault_type, alert_level)
    if alert_identifier in active_alerts:
        return  # Alert has already been sent; no need to notify again

    # Add the alert identifier to the active alerts set
    active_alerts.add(alert_identifier)

    # Construct the payload for the alert
    url = "http://localhost:8000/trigger_alert"  # Corrected URL for trigger_alert endpoint
    data = {
        "alert_title": fault_type,  # Assign fault_type to alert_title
        "alert_message": alert_message,  # Include the full alert message
        "field_name": field_name,  # Set the corresponding field name
        "lower_bound": None,  # Set bounds if applicable; can be adjusted as needed
        "higher_bound": None
    }

    # Debugging: Print the payload to verify
    print("Sending alert data:", data)

    # Send the POST request
    response = requests.post(url, json=data)

    # Check the response status
    if response.status_code != 200:
        print("Error notifying alert:", response.text)

# Reset active alerts after a period (optional)
def reset_alerts():
    global active_alerts
    active_alerts.clear()

# Step 5: Main Loop
def main():
    setup_database()  # Set up the database at the start

    while True:
        fault_type, alert_level, alert_message = detect_faults()
        if fault_type:
            log_fault(fault_type, alert_level, alert_message)
            notify_fault(fault_type, alert_level, alert_message)  # Notify using print statements
        
        time.sleep(5)  # Wait for 5 seconds before checking again

        # Optional: Reset alerts every minute or so
        if time.time() % 60 < 5:  # Resets every minute
            reset_alerts()


if __name__ == "__main__":
    main()  # This starts the main function when the script is run directly
