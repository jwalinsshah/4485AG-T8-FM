import sqlite3
import random
import time

# Step 1: Set Up the SQLite Database
def setup_database():
    conn = sqlite3.connect('5g_fault_management.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faults
                 (timestamp TEXT, fault_type TEXT, details TEXT)''')
    conn.commit()
    conn.close()

# Step 2: Fault Detection Function
def detect_faults():
    # Simulate 5G metrics
    latency = random.uniform(1.0, 100.0)  # in milliseconds
    signal_strength = random.uniform(-120.0, -40.0)  # in dBm
    packet_loss = random.uniform(0.0, 5.0)  # in percentage

    # Define thresholds for faults
    if latency > 50.0:
        return "High Latency", f"Latency: {latency:.2f} ms"
    elif signal_strength < -100.0:
        return "Poor Signal Strength", f"Signal Strength: {signal_strength:.2f} dBm"
    elif packet_loss > 2.0:
        return "High Packet Loss", f"Packet Loss: {packet_loss:.2f}%"
    
    return None, None  # No fault detected

# Step 3: Fault Logging Function
def log_fault(fault_type, details):
    conn = sqlite3.connect('5g_fault_management.db')
    c = conn.cursor()
    c.execute("INSERT INTO faults (timestamp, fault_type, details) VALUES (?, ?, ?)",
              (time.ctime(), fault_type, details))
    conn.commit()
    conn.close()

# Step 4: Notify Fault through Print Statements
def notify_fault(fault_type, details):
    alert_message = f"ALERT: {fault_type} - {details}"
    print(alert_message)  # Print to console for immediate feedback

# Step 5: Main Loop
def main():
    setup_database()  # Set up the database at the start

    while True:
        fault_type, details = detect_faults()
        if fault_type:
            log_fault(fault_type, details)
            notify_fault(fault_type, details)  # Notify using print statements
        
        time.sleep(5)  # Wait for 5 seconds before checking again

if __name__ == "__main__":
    main()  # This starts the main function when the script is run directly
