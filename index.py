from fastapi import FastAPI, Form
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


# Incoming webhook payload from Statuspage
class StatusEvent(BaseModel):
    incident: dict | None = None
    component: dict | None = None


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


@app.post("/webhook")
async def webhook(event: StatusEvent):
    # INCIDENT UPDATE
    if event.incident:
        inc = event.incident
        name = inc.get("name", "Unknown Incident")
        status = inc.get("status", "Unknown Status")
        update_msg = inc.get("incident_updates", [{}])[0].get("body", "")

        log(f"Product: {name}")
        log(f"Status: {status}")
        log(f"Event: {update_msg}")
        print("--------------------------------------------------")
        return {"ok": True}

    # COMPONENT STATUS CHANGE
    if event.component:
        comp = event.component
        name = comp.get("name", "Unknown Component")
        status = comp.get("status", "Unknown Status")

        log(f"Product: {name}")
        log(f"Status: {status}")
        print("--------------------------------------------------")
        return {"ok": True}

    # Unknown payload
    log("Unknown webhook event received")
    print(event.dict())
    return {"ok": True}


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


@app.post("/email-webhook")
async def email_webhook(
    subject: str = Form(...),
    from_email: str = Form(..., alias="from"),
    body_text: str = Form(..., alias="text")
):
    """
    Receives incident update emails from OpenAI Status Page
    through an inbound email-to-webhook service.
    """

    log("EMAIL RECEIVED")
    log(f"From: {from_email}")
    log(f"Subject: {subject}")
    log(f"Body: {body_text}")

    # Basic parsing of subject line
    # Example: "[OpenAI API] Major Outage - Chat Completions"
    product = "Unknown Product"
    status = "Unknown Status"

    # Try parsing simple subject pattern
    if "OpenAI" in subject:
        parts = subject.replace("[", "").replace("]", "").split(" - ")
        if len(parts) >= 2:
            product = parts[0].strip()
            status = parts[1].strip()

    # Print final log
    log(f"Product: {product}")
    log(f"Status: {status}")
    log(f"Event: {body_text.splitlines()[0]}")
    print("--------------------------------------------------")

    return {"ok": True}
