import pandas as pd
from fasthtml.common import *
import time
import threading
import json
from starlette.requests import Request
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import asyncio

app = FastHTML()

# Global variables to track alert level and last alert time
alert_level = "green"
alert_message = "All processes are working correctly."
last_alert_time = None

# Function to generate the HTML response with the alert panel
def generate_html(request, alert_level: str, alert_message: Optional[str] = None):

    print(alert_level)
    print(alert_message)

    if alert_level == "green":
        text_color = "white"
    else:
        text_color = "black"

    # Create the title of the site
    title = H1("Fault Management System", style="text-align: center;")

    alert_config = Div(
        Div(
            H2("Add Alert"),
            P("Configure an alert with the button below:"),
            Button("Add Alert", id="alert-button"),
            cls="column",
            style="width: 45%; background-color: lightblue; padding: 20px; text-align: center;"
        ),
        Div(
            H2("Configure Alerts"),
            P("Configure your added alerts here."),
            P("Settings options..."),
            cls="column",
            style="width: 45%; background-color: lightblue; padding: 20px; text-align: center;"
        ),
        cls="row",
        style="display: flex; justify-content: center;"
    )

    # Create the HTML structure with the alert panel
    alert_panel = Div(
        H2("Alert notifications appear here."),
        Div(
        alert_message,
        id="alert-panel",  # Set the ID to "alert-panel"
        style=f"padding: 10px; border: 1px solid black; background-color: {alert_level}; color: {text_color}; text-align: center;"
        )
    )

    js_code = """function fetchAndUpdate() {
                    fetch('/get_alert_data')
                        .then(response => response.json())
                        .then(data => {
                            // Update the UI with the received data
                            const alertPanel = document.getElementById("alert-panel");
                            alertPanel.textContent = data.alert_message;
                            alertPanel.style.backgroundColor = data.alert_level;
                            alertPanel.style.color = data.alert_level === "green" ? "white" : "black";
                        })
                        .catch(error => {
                            console.error("Error fetching data:", error);
                        });
                }

                setInterval(fetchAndUpdate, 1000); // Fetch data every second"""

    # Include the JavaScript script
    script_tag = Script(code=js_code)

    return Html(title, Hr(), alert_config, alert_panel, script_tag)

# Function to handle the alert logic
async def handle_alert(alert_level: str, alert_message: Optional[str] = None):
    global last_alert_time

    print(last_alert_time)

    # Set the alert level and message
    last_alert_time = time.time()
    return True

# Function to manage alerts in a separate thread
async def alert_manager():

    while True:
        await asyncio.sleep(0.1)
        global last_alert_time
        global alert_message
        global alert_level


# Start the alert manager thread
alert_thread = threading.Thread(target=alert_manager)
alert_thread.start()

# Route for the main page
@app.get("/")
async def home(request: Request):
    global alert_message
    global alert_level

    return generate_html(request, alert_level, alert_message)

# Endpoint to handle POST requests and trigger alerts
@app.post("/trigger_alert")
async def trigger_alert(request: Request):
    global alert_message
    global alert_level
    try:
        data = await request.json()

        alert_level = data.get("alert_level", "green")
        alert_message = data.get("alert_message", "All processes are working correctly.")

        print(alert_level)
        print(alert_message)

        await handle_alert(alert_level, alert_message)

        return {"message": "Alert triggered successfully"}
    except Exception as e:
        return {"error": f"Invalid JSON data provided: {e}"}
    
# Endpoint to handle GET requests for alert data
@app.get("/get_alert_data")
async def get_alert_data():
    global last_alert_time
    global alert_level
    global alert_message
    print(time.time())
    if last_alert_time and time.time() - last_alert_time > 3:
        last_alert_time = None
        alert_level = "green"
        alert_message = "All processes are working correctly."
        print("Resetting alert")

    return {"alert_level": alert_level, "alert_message": alert_message}
    

serve()