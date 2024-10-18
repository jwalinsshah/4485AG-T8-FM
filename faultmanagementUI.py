# FastHTML Application Code
from fasthtml.common import *
from pydantic import BaseModel
from typing import Optional, List
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi import File, UploadFile
import sqlite3
import json

app, rt = fast_app(
    live=True,
)

# Add session middleware with a secret key
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")  # Replace with your actual secret key

alert_level = "green"
alert_message = "All processes are working correctly."

schema_data = []
alerts = []
triggered_alerts = []

# Used to display database schema information to the user.
class SchemaData(BaseModel):
    field_name: str
    data_type: str

class Alert(BaseModel):
    alert_title: str
    alert_message: str
    field_name: str
    lower_bound: Optional[float] = None
    higher_bound: Optional[float] = None

# Endpoint to handle database upload
uploaded_db_file = None  # Global variable to store uploaded database file path

@rt('/')
def get():
    
    # Include Bootstrap CSS and JS
    bootstrap_css = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css", integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T", crossorigin="anonymous")
    jQuery_js = Script(src="https://code.jquery.com/jquery-3.3.1.slim.min.js", integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo", crossorigin="anonymous")
    popper_js = Script(src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js", integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1", crossorigin="anonymous")
    bootstrap_js = Script(src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js", integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM", crossorigin="anonymous")

    title = "Super Fault Management System"
    schema_data = [
            SchemaData(field_name="latency", data_type="FLOAT"),
            SchemaData(field_name="signal_strength", data_type="FLOAT"),
            SchemaData(field_name="packet_loss", data_type="FLOAT")
    ]
    # Database upload form
    database_upload_form = Div(
        H2("Upload Database"),
        Form(
            Input(type="file", id="database_file", name="database_file", accept=".db"),
            Button("Upload", type="submit"),
            enctype="multipart/form-data",
            hx_post="/upload_database",
            hx_target="#table-selector-div",
            hx_swap="innerHTML",
            style="padding: 5px; text-align: center;"
        )
    )

    # Div to hold table selector
    table_selector_div = Div(
        id="table-selector-div",
        style="padding: 5px; text-align: center;"
    )

    # Div to display database schema
    database_schema_div = Div(
        id='database-schema-div',
        style='padding: 5px; text-align: center;'
    )

    # Schema upload form
    schema_upload_form = Div(
        H2("Upload Schema Data"),
        Form(
            Textarea(id="schema-data", name="schema_data", placeholder="Enter schema data here...", rows=10, cols=50),
            Button("Upload Schema", type="submit"),
            hx_post="/upload_schema",
            hx_target="#database-schema-div",
            hx_swap="innerHTML",
            style="padding: 5px; text-align: center;"
        )
    )

    # Alert configuration
    alert_config = Div(
        Div(
            H2("Add an Alert:"),
            Form(
                Input(type="text", id="alert_title", placeholder="Alert Title", required=True),
                Input(type="text", id="alert_message", name="alert_message", placeholder="Alert Message", required=True),
                Select(
                    *[Option(field.field_name, value=field.field_name) for field in schema_data],
                    id="field-selector",
                    name="field_name",
                    required=True
                ),
                Input(type="number", id="lower_bound", name="lower_bound", placeholder="Lower Bound"),
                Input(type="number", id="higher_bound", name="higher_bound", placeholder="Higher Bound"),
                Button("Add Alert", id="alert-button", type="submit"),
                hx_post="/add_alert",
                hx_trigger="click",
                hx_target="#active-alerts",
                hx_swap="innerHTML",  # Swap only the content inside the alerts div
                style="padding: 5px; text-align: center;"
            )
        ),
        Div(
            H2("Active Alerts"),
            Div(
                *[
                    Div(
                        f"{alert.alert_title}: {alert.alert_message} (Field: {alert.field_name}, Bounds: {alert.lower_bound} - {alert.higher_bound})",
                        Button("x", hx_post="/remove_alert", hx_trigger="click", hx_vals=f'{{"index": {index}}}', hx_target="#active-alerts", hx_swap="innerHTML", style="margin-left: 10px;"),
                        style="padding: 5px; border: 1px solid black; margin: 5px;"
                    )
                    for index, alert in enumerate(alerts)
                ],
                id="active-alerts",
                style="width: 50%; margin: auto;"
            ),
            style="width: 50%;"
        ),
        cls="row",
        style="display: flex; justify-content: center;"
    )

    # Alert container
    alert_container = Div(
        id='alert-container',
        hx_get='/new_data',
        hx_trigger='every 3s',
    )

    # return Titled(
    #     title,
    #     Hr(),
    #     database_upload_form,
    #     table_selector_div,
    #     database_schema_div,
    #     Hr(),
    #     schema_upload_form,
    #     Hr(),
    #     alert_config,
    #     Hr(),
    #     alert_container,
    #     alert_notifications,
    #     style="text-align: center;"
    
    # )
    
    return Titled(
        title, 
        Head(
            # bootstrap_css,
            jQuery_js,
            popper_js,
            bootstrap_js
        ),
        Hr(), 
        database_schema_div, 
        table_selector_div, 
        Hr(),
        schema_upload_form,
        Hr(), 
        alert_config, 
        Hr(), 
        alert_container,
        style="text-align: center;")


@app.post("/upload_database")
async def upload_database(database_file: UploadFile = File(...), request: Request = None):
    global uploaded_db_file

    # Save the uploaded file
    file_location = f"./{database_file.filename}"
    with open(file_location, "wb") as f:
        f.write(await database_file.read())

    # Store the file path in session
    request.session['uploaded_db_file'] = file_location
    uploaded_db_file = file_location

    # Connect to the database and fetch table names
    conn = sqlite3.connect(file_location)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()

    # Return a table selector
    return Select(
        *[Option(table[0], value=table[0]) for table in tables],
        id='table-selector',
        hx_post='/select_table',
        hx_target='#database-schema-div',
        hx_swap='innerHTML',
        hx_trigger='change',
        style="margin-top: 10px;"
    )

@app.post("/select_table")
async def select_table(request: Request):
    form_data = await request.form()
    table_name = form_data.get('table-selector')

    # Get the uploaded database file path from session
    uploaded_db_file = request.session.get('uploaded_db_file', None)

    if not uploaded_db_file:
        return Div("No database file uploaded.", style="color: red;")

    # Connect to the database and get the table schema
    conn = sqlite3.connect(uploaded_db_file)
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table_name});")
    schema_info = c.fetchall()
    conn.close()

    # Generate schema table
    table = Table(
        Tr(
            Th("Column Name", style="border: 1px solid black; font-weight: bold;"),
            Th("Data Type", style="border: 1px solid black; font-weight: bold;"),
            Th("Not Null", style="border: 1px solid black; font-weight: bold;"),
            Th("Default Value", style="border: 1px solid black; font-weight: bold;"),
            Th("Primary Key", style="border: 1px solid black; font-weight: bold;"),
        ),
        style="border: 1px solid black; margin: auto;"
    )

    for column in schema_info:
        # column = (cid, name, type, notnull, dflt_value, pk)
        table += Tr(
            Td(column[1], style="border: 1px solid black;"),
            Td(column[2], style="border: 1px solid black;"),
            Td("Yes" if column[3] else "No", style="border: 1px solid black;"),
            Td(column[4] if column[4] else "", style="border: 1px solid black;"),
            Td("Yes" if column[5] else "No", style="border: 1px solid black;"),
        )

    return Div(
        H4(f"Schema of table: {table_name}"),
        table,
        style="padding: 5px; text-align: center;"
    )

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
        return Div("Schema data received successfully.", style="color: green;")
    except Exception as e:
        return Div(f"Error parsing schema data: {e}", style="color: red;")

@app.post("/add_alert")
async def add_alert(request: Request):
    form_data = await request.form()

    alert = Alert(
        alert_title=form_data.get("alert_title"),
        alert_message=form_data.get("alert_message"),
        field_name=form_data.get("field_name"),
        lower_bound=float(form_data.get("lower_bound")) if form_data.get("lower_bound") else None,
        higher_bound=float(form_data.get("higher_bound")) if form_data.get("higher_bound") else None,
    )

    # Add the alert to the alerts list
    alerts.append(alert)
    print(alerts)

    # Generate the HTML for the updated list of alerts
    html_alerts = [
        Div(
            f"{alert.alert_title}: {alert.alert_message} (Field: {alert.field_name}, Bounds: {alert.lower_bound} - {alert.higher_bound})",
            Button("x", hx_post="/remove_alert", hx_trigger="click", hx_vals=f'{{"index": {index}}}', hx_target="#active-alerts", hx_swap="innerHTML", style="margin-left: 10px;"),
            style="padding: 5px; border: 1px solid black; margin: 5px;"
        )
        for index, alert in enumerate(alerts)
    ]

    return html_alerts

@app.post("/remove_alert")
async def remove_alert(request: Request):
    data = await request.form()
    index = data.get("index")
    if index is not None and 0 <= int(index) < len(alerts):
        alerts.pop(int(index))
        html_alerts = [
            Div(
                f"{alert.alert_title}: {alert.alert_message} (Field: {alert.field_name}, Bounds: {alert.lower_bound} - {alert.higher_bound})",
                Button("x", hx_post="/remove_alert", hx_trigger="click", hx_vals=f'{{"index": {idx}}}', hx_target="#active-alerts", hx_swap="innerHTML", style="margin-left: 10px;"),
                style="padding: 5px; border: 1px solid black; margin: 5px;"
            )
            for idx, alert in enumerate(alerts)
        ]
        return html_alerts
    return Div("Invalid alert index.", style="color: red;")

@app.post("/new_data")
async def new_data(data: dict):
    global alert_level, alert_message, triggered_alerts

    print('New data received:', data)

    for alert in alerts:
        field_value = data.get(alert.field_name)
        if field_value is not None:
            if (alert.lower_bound is not None and field_value < alert.lower_bound) or \
                (alert.higher_bound is not None and field_value > alert.higher_bound):
                triggered_alerts.append(alert)
    
@app.get("/new_data")
async def get_alerts():
    global alert_level, alert_message, triggered_alerts

    if triggered_alerts:
        alert_level = "red"
        alert_message = "Multiple alerts triggered"

        print("Alerts triggered!!!!!!!!:", triggered_alerts)

       # Generate the dismissible alert HTML
        dismissible_alerts_html = "".join([
            f"""
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <strong>{alert.alert_title}!</strong> {alert.alert_message}.
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            """
            for alert in triggered_alerts
        ])
        # Return an HTML update instruction for HTMX to update the alert
        return dismissible_alerts_html
    else:
        alert_level = "green"
        alert_message = "All processes are working correctly."
        return ""


@app.get("/api/alerts")
async def get_alerts_api():
    return alerts

# Endpoint to process fault submissions (if needed)
@app.post("/submit_fault")
async def submit_fault(fault_data: dict):
    # Process the submitted fault and add it to the database or trigger alerts
    # You can extend this to analyze the fault and notify relevant parties
    return {"message": "Fault data processed successfully"}

serve()
