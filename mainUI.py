# Necessary pip installs:
# pip install fastapi python-jose requests python-dotenv uvicorn

from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from jose import jwt, JWTError
from pydantic import BaseModel
import requests
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import sqlite3
import json

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]

# OAuth2 URL for Auth0
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{AUTH0_DOMAIN}/oauth/token"
)

# Custom JWT validation
def verify_jwt(token: str = Depends(oauth2_scheme)):
    try:
        header = jwt.get_unverified_header(token)
        rsa_key = get_rsa_key(header)
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def get_rsa_key(header):
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    for key in jwks["keys"]:
        if key["kid"] == header["kid"]:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    return None

# Define restricted endpoint
@app.get("/restricted")
async def restricted_access(payload: dict = Depends(verify_jwt)):
    return {"message": "You have access", "payload": payload}

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

# Route to handle new data
@app.post("/new_data")
async def receive_new_data(data: dict):
    print("Received new data:", data)
    return {"message": "Data received successfully"}

# Route to trigger an alert
@app.post("/trigger_alert")
async def trigger_alert(alert: Alert):
    global alerts, alert_level, alert_message
    print(f"Alert triggered: Title - {alert.alert_title}, Message - {alert.alert_message}")

    # Update alert status
    alerts.append(alert)
    alert_level = "yellow"  # Assuming triggered alerts change the level to yellow
    alert_message = alert.alert_message

    return {"message": "Alert received successfully", "alert": alert}

# To run the app, use `uvicorn` from the command line
# Command: uvicorn mainUI:app --reload
