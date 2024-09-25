import sqlite3
import random
import time
import smtplib
from email.mime.text import MIMEText

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
        return "High Latency", f"Latency: {latency} ms"
    elif signal_strength < -100.0:
        return "Poor Signal Strength", f"Signal Strength: {signal_strength} dBm"
    elif packet_loss > 2.0:
        return "High Packet Loss", f"Packet Loss: {packet_loss}%"
    
    return None, None  # No fault detected

# Step 3: Fault Logging Function
def log_fault(fault_type, details):
    conn = sqlite3.connect('5g_fault_management.db')
    c = conn.cursor()
    c.execute("INSERT INTO faults (timestamp, fault_type, details) VALUES (?, ?, ?)",
              (time.ctime(), fault_type, details))
    conn.commit()
    conn.close()

# Step 4: Email Notification Function
def send_email_alert(subject, body, to_email):
    from_email = "your_email@example.com"  # Replace with your email
    password = "your_password"  # Use app-specific password if using Gmail

    # Create the email
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Send the email
    with smtplib.SMTP('smtp.example.com', 587) as server:  # Replace with your SMTP server
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

# Step 5: Modify Notification Function
def notify_fault(fault_type, details, user_email):
    alert_message = f"ALERT: {fault_type} - {details}"
    print(alert_message)  # Print to console for immediate feedback
    send_email_alert(f"Fault Detected: {fault_type}", alert_message, user_email)

# Step 6: Main Loop
def main():
    setup_database()  # Set up the database at the start

    user_email = "jshah1331@gmail.com"  # Replace with the user's email address

    while True:
        fault_type, details = detect_faults()
        if fault_type:
            log_fault(fault_type, details)
            notify_fault(fault_type, details, user_email)
        
        time.sleep(5)  # Wait for 5 seconds before checking again

if __name__ == "__main__":
    main()
