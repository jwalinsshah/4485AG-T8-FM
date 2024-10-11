from fasthtml.common import *
from pydantic import BaseModel
from typing import Optional

app, rt = fast_app(live=True)

alert_level = "green"
alert_message = "All processes are working correctly."

schema_data = []
alerts = []

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

# Waits for a POST request once the schema is read.
@app.post("/upload_schema")
async def upload_schema(data: list[SchemaData]):
    global schema_data
    schema_data = data
    return {"message": "Schema data received successfully"}

# Returns a table with database schema information.
def generate_schema_table():
    table = Table(
        Tr(
            Th("Field Name", style="border: 1px solid white; font-weight: bold;"),
            Th("Data Type", style="border: 1px solid white; font-weight: bold;"),
        ),
        style="border: 1px solid white;"
    )

    for field in schema_data:
        table += Tr(
            Td(field.field_name, style="border: 1px solid white;"),
            Td(field.data_type, style="border: 1px solid white;"),
            style="border: 1px solid white;"
        )

    return table

@rt('/')
def get():
    global schema_data

    title = "Super Cool Fault Management System"

    #TODO: Use a pre-defined schema for the database. THIS IS FOR TESTING
    schema_data = [
        SchemaData(field_name="latency", data_type="FLOAT"),
        SchemaData(field_name="signal_strength", data_type="FLOAT"),
        SchemaData(field_name="packet_loss", data_type="FLOAT")
    ]

    table = generate_schema_table() # returns a table to display in the get endpoint

    database_schema = Div(
        H4("Database Schema"),
        Table(
            id="database-schema",
            cls="table",
            style="width: 50%; margin: auto;",
        )
    )

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

    alert_notifications = Div(
        Div(
            H2("Alert Notifications"),
            hx_get="/new_data",
            hx_target="#alert-container",
            hx_swap="outerHTML",
            style="margin: 20px;",
            hx_trigger="interval:5000"
        ),
        id="alert-container",
    )

    return Titled(title, Hr(), database_schema, table, Hr(), alert_config, Hr(), alert_notifications, style="text-align: center;")

@app.post("/remove_alert")
async def remove_alert(data: dict):
    index = data.get("index")
    if index is not None and 0 <= int(index) < len(alerts):
        alerts.pop(int(index))
        html_alerts = "".join(
            f"""
            <div style="padding: 5px; border: 1px solid black; margin: 5px;">
                {alert.alert_title}: {alert.alert_message} (Field: {alert.field_name}, Bounds: {alert.lower_bound} - {alert.higher_bound})
                <button onclick="removeAlert({idx})" style="margin-left: 10px;">x</button>
            </div>
            """
            for idx, alert in enumerate(alerts)
        )
        return # {"success": True, "html": html_alerts}
    return # {"success": False}

@app.post("/add_alert")
async def add_alert(alert: Alert):
    # Add the alert to the alerts list
    alerts.append(alert)

    # Generate the HTML for the updated list of alerts
    html_alerts = "".join(
        f"""
        <div style="padding: 5px; border: 1px solid black; margin: 5px;">
            {alert.alert_title}: {alert.alert_message} (Field: {alert.field_name}, Bounds: {alert.lower_bound} - {alert.higher_bound})
            <button hx-post="/remove_alert" hx-trigger="click" hx-vals='{{"index": {index}}}' hx-target="#active-alerts" hx-swap="innerHTML" style="margin-left: 10px;">x</button>
        </div>
        """
        for index, alert in enumerate(alerts)
    )

    # Return the generated HTML for the alerts
    return html_alerts

@app.post("/new_data")
async def new_data(data: dict):
    global alert_level, alert_message

    print('New data received:', data)

    # Loop through all alerts and check if any alert conditions are triggered
    for alert in alerts:
        field_value = data.get(alert.field_name)
        if field_value is not None:
            if (alert.lower_bound is not None and field_value < alert.lower_bound) or \
                (alert.higher_bound is not None and field_value > alert.higher_bound):
                alert_level = "red"
                alert_message = f"Alert: {alert.alert_title} - {alert.alert_message}"

                # Generate a dismissible alert HTML
                dismissible_alert_html = f"""
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong>{alert.alert_title}!</strong> {alert.alert_message}.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
                """
                return dismissible_alert_html

    # No alerts triggered, reset alert level and message
    alert_level = "green"
    alert_message = "All processes are working correctly."

    # No alert to show, return an empty string
    return ""

serve()
