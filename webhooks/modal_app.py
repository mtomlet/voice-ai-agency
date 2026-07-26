import modal
import json
import os
from datetime import datetime

app = modal.App("lead-reactivation-webhooks")

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "gspread",
    "google-auth",
    "requests",
)

GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDS_JSON", "")

SPREADSHEET_ID = "15Ts0s0yImp6Hv_9SuygU4xg-gpJd-Ao1Q2I9fBouuPw"
SHEET_NAME = "lead-reactivation-sheet"
RETELL_API_KEY = os.environ.get("RETELL_API_KEY", "")


def get_sheet():
    """Get authenticated Google Sheet."""
    import gspread
    from google.oauth2.service_account import Credentials

    creds_dict = json.loads(GOOGLE_CREDS_JSON)
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets"
    ])
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet.worksheet(SHEET_NAME)


def normalize_phone(phone):
    """Strip to last 10 digits for matching."""
    import re
    digits = re.sub(r'\D', '', phone or '')
    return digits[-10:] if len(digits) >= 10 else digits


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

web_app = FastAPI()


# ════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════
@web_app.get("/")
async def health():
    return {
        "status": "running",
        "service": "Lead Reactivation Webhooks",
        "endpoints": {
            "GET /next-call": "Call the next uncalled lead (hit every 5 min)",
            "POST /pre-call": "Look up lead context by phone number",
            "POST /post-call": "Retell webhook — updates Google Sheet after each call",
        }
    }


# ════════════════════════════════════════
# WEBHOOK 1: PRE-CALL — Lead Context Lookup
# ════════════════════════════════════════
# For outbound calls: called by /trigger-calls before creating each call.
# For inbound routing: Retell sends { "from_number": "+1..." }
@web_app.post("/pre-call")
async def pre_call(request: Request):
    try:
        body = await request.json()
        incoming_phone = normalize_phone(
            body.get("phone_number") or body.get("from_number") or body.get("to_number") or ""
        )
        if not incoming_phone:
            return JSONResponse(status_code=400, content={"error": "No phone number provided"})

        sheet = get_sheet()
        records = sheet.get_all_records()

        for row in records:
            if normalize_phone(str(row.get("phone_number", ""))) == incoming_phone:
                print(f"[PRE-CALL] Found: {row['first_name']} {row['last_name']} ({incoming_phone})")
                return {
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                    "phone_number": row.get("phone_number", ""),
                    "lead_source": row.get("lead_source", ""),
                    "original_interest": row.get("original_interest", ""),
                    "agent_name": row.get("agent_name", ""),
                    "transfer_number": row.get("transfer_number", ""),
                }

        return JSONResponse(status_code=404, content={"error": "Lead not found", "phone": incoming_phone})

    except Exception as e:
        print(f"[PRE-CALL] Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ════════════════════════════════════════
# WEBHOOK 2: POST-CALL — Update Google Sheet
# ════════════════════════════════════════
# Retell sends webhook events: call_started, call_ended, call_analyzed
# We act on call_analyzed to write post-call data back to the sheet.
@web_app.post("/post-call")
async def post_call(request: Request):
    try:
        body = await request.json()
        event = body.get("event", "")

        # Only process call_analyzed events (contains post-call analysis)
        if event == "call_started":
            return {"status": "acknowledged", "event": event}

        call = body.get("call", {})
        call_analysis = call.get("call_analysis", {})
        custom_data = call_analysis.get("custom_analysis_data", {})

        # For outbound calls, to_number is the lead's phone
        lead_phone = normalize_phone(call.get("to_number", "") or call.get("from_number", ""))
        if not lead_phone:
            return JSONResponse(status_code=400, content={"error": "No phone number in call data"})

        sheet = get_sheet()
        records = sheet.get_all_records()
        headers = sheet.row_values(1)

        # Find the row
        row_index = None
        for i, row in enumerate(records):
            if normalize_phone(str(row.get("phone_number", ""))) == lead_phone:
                row_index = i + 2  # +1 for header, +1 for 1-indexed
                break

        if row_index is None:
            return JSONResponse(status_code=404, content={"error": "Lead not found", "phone": lead_phone})

        # Build update values for columns I through Q
        today = datetime.now().strftime("%Y-%m-%d")

        # Extract from custom analysis data or fall back to call-level data
        call_status = custom_data.get("call_status", "")
        if not call_status:
            # Infer from call data
            in_voicemail = call_analysis.get("in_voicemail", False)
            if in_voicemail:
                call_status = "voicemail"
            elif call.get("disconnection_reason") == "dial_no_answer":
                call_status = "no_answer"
            elif call.get("transcript"):
                call_status = "answered"

        updates = [
            call_status,
            custom_data.get("interest_level", ""),
            custom_data.get("timeline", ""),
            custom_data.get("pre_approved", ""),
            custom_data.get("working_with_agent", ""),
            custom_data.get("transfer_attempted", ""),
            custom_data.get("notes", call_analysis.get("call_summary", "")),
            custom_data.get("next_action", ""),
            today,
        ]

        # Update columns I through Q (columns 9-17)
        col_start = headers.index("call_status") + 1  # 1-indexed
        for j, val in enumerate(updates):
            sheet.update_cell(row_index, col_start + j, str(val))

        # Write recording URL as a playable hyperlink in the "recording" column
        recording_url = call.get("recording_url", "")
        if recording_url:
            if "recording" in headers:
                rec_col = headers.index("recording") + 1
            else:
                rec_col = len(headers) + 1
                sheet.update_cell(1, rec_col, "recording")
            # HYPERLINK opens in browser's native audio player instead of downloading
            formula = f'=HYPERLINK("{recording_url}", "▶ Play Recording")'
            sheet.update_cell(row_index, rec_col, formula)

        print(f"[POST-CALL] Updated: {lead_phone} -> {call_status} / {custom_data.get('interest_level', 'unknown')}")
        return {"success": True, "row": row_index, "phone": lead_phone, "recording": recording_url or "none"}

    except Exception as e:
        print(f"[POST-CALL] Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ════════════════════════════════════════
# AUTO-DIALER: Runs every 5 minutes
# ════════════════════════════════════════
# Reads the sheet, finds the next uncalled lead, calls them.
# Stops automatically when there are no uncalled leads left.

def call_next_lead():
    """Core logic: find next uncalled lead, call them via Retell."""
    import requests as req

    FROM_NUMBER = "+17579415876"
    AGENT_ID = "agent_d09396520d5ef0a38b275b6747"

    sheet = get_sheet()
    records = sheet.get_all_records()

    # Find the first uncalled lead
    lead = None
    for row in records:
        if not row.get("call_status"):
            phone = str(row.get("phone_number", ""))
            if phone:
                lead = row
                break

    if not lead:
        print("[AUTO-DIALER] No uncalled leads remaining. List complete.")
        return {"status": "done", "remaining": 0}

    raw_phone = str(lead["phone_number"]).strip()
    name = lead.get("first_name", "Unknown")
    print(f"[AUTO-DIALER] Raw phone from sheet: '{raw_phone}' (len={len(raw_phone)})")

    # Ensure E.164 format — Sheets strips the + and stores as int
    # Clean any non-digit chars except leading +
    digits = ''.join(c for c in raw_phone if c.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        phone = f"+{digits}"
    elif len(digits) == 10:
        phone = f"+1{digits}"
    else:
        phone = f"+{digits}"
    print(f"[AUTO-DIALER] Formatted phone: '{phone}'")

    # Format transfer number the same way
    raw_transfer = str(lead.get("transfer_number", "")).strip()
    transfer_digits = ''.join(c for c in raw_transfer if c.isdigit())
    if len(transfer_digits) == 11 and transfer_digits.startswith("1"):
        transfer = f"+{transfer_digits}"
    elif len(transfer_digits) == 10:
        transfer = f"+1{transfer_digits}"
    else:
        transfer = f"+{transfer_digits}"

    # Pass lead context as dynamic variables
    payload = {
        "from_number": FROM_NUMBER,
        "to_number": phone,
        "override_agent_id": AGENT_ID,
        "retell_llm_dynamic_variables": {
            "first_name": str(lead.get("first_name", "")),
            "last_name": str(lead.get("last_name", "")),
            "phone_number": phone,
            "lead_source": str(lead.get("lead_source", "")),
            "original_interest": str(lead.get("original_interest", "")),
            "agent_name": str(lead.get("agent_name", "Mike Thompson")),
            "transfer_number": transfer,
        },
    }

    resp = req.post(
        "https://api.retellai.com/v2/create-phone-call",
        headers={
            "Authorization": f"Bearer {RETELL_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    remaining = sum(1 for r in records if not r.get("call_status")) - 1

    if resp.status_code == 201:
        call_id = resp.json().get("call_id", "")
        print(f"[AUTO-DIALER] Calling {name} at {phone} — call_id: {call_id} — {remaining} remaining")
        return {"status": "calling", "name": name, "phone": phone, "call_id": call_id, "remaining": remaining}
    else:
        print(f"[AUTO-DIALER] Failed {name} at {phone}: {resp.text}")
        return {"status": "error", "name": name, "phone": phone, "error": resp.text, "remaining": remaining}


# Scheduled function — runs every 5 minutes automatically
@app.function(image=image, secrets=[modal.Secret.from_name("voice-ai-agency")])
def auto_dialer():
    """Auto-dialer (paused). Re-add schedule=modal.Cron("*/5 * * * *") to reactivate."""
    result = call_next_lead()
    print(f"[AUTO-DIALER] Result: {result}")
    return result


# Manual trigger via web endpoint (same logic, for testing)
@web_app.get("/next-call")
async def next_call():
    try:
        result = call_next_lead()
        return result
    except Exception as e:
        print(f"[NEXT-CALL] Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.function(image=image, min_containers=1, secrets=[modal.Secret.from_name("voice-ai-agency")])
@modal.asgi_app()
def webhook_server():
    return web_app
