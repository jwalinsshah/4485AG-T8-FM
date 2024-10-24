from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import json
import os

# Initialize FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Global variables for alerts and schema data
alert_level = "green"
alert_message = "All processes are working correctly."
schema_data = []
alerts = []
triggered_alerts = []

# Pydantic models for schema and alerts
class SchemaData(BaseModel):
    field_name: str
    data_type: str

class Alert(BaseModel):
    alert_title: str
    alert_message: str
    field_name: str
    lower_bound: Optional[float] = None
    higher_bound: Optional[float] = None

# Global variable to store uploaded database file path
uploaded_db_file = None

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    # Render the HTML page with the schema data and alert info
    return templates.TemplateResponse("index.html", {
        "request": request,
        "schema_data": schema_data,
        "alerts": alerts,
        "alert_level": alert_level,
        "alert_message": alert_message
    })

@app.post("/upload_database")
async def upload_database(database_file: UploadFile = File(...), request: Request = None):
    global uploaded_db_file

    # Save the uploaded file securely
    file_location = f"./{database_file.filename}"
    with open(file_location, "wb") as f:
        f.write(await database_file.read())

    # Store the file path in a global variable
    uploaded_db_file = file_location

    # Connect to the database and fetch table names
    try:
        conn = sqlite3.connect(file_location)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        conn.close()

        # Optionally, return the list of tables as part of the response
        return HTMLResponse(f"Database uploaded successfully. Tables: {', '.join([table[0] for table in tables])}")
    except Exception as e:
        return HTMLResponse(f"Error connecting to the database: {e}")

@app.post("/upload_schema")
async def upload_schema(request: Request):
    global schema_data
    form_data = await request.form()
    schema_text = form_data.get("schema_data")

    # Parse the schema text into SchemaData objects
    try:
        # Assume schema is in JSON format
        schema_list = json.loads(schema_text)
        schema_data = [SchemaData(**field) for field in schema_list]
        return HTMLResponse("Schema data received successfully.")
    except Exception as e:
        return HTMLResponse(f"Error parsing schema data: {e}")

# Other routes (add alerts, select table, etc.) can be defined here
@app.post("/new_data")
async def receive_new_data(data: dict):
    # Process the incoming data here
    print("Received new data:", data)
    return {"message": "Data received successfully"}

class Alert(BaseModel):
    alert_level: str
    alert_message: str

@app.post("/trigger_alert")
async def trigger_alert(alert: Alert):
    print(f"Alert triggered: Level - {alert.alert_level}, Message - {alert.alert_message}")
    return {"message": "Alert received successfully"}

# To run the app, use `uvicorn` from the command line
# Command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
