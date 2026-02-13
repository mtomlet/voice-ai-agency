import modal
import json
import os
from datetime import datetime

app = modal.App("airbnb-calendar-check")

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "google-auth",
    "google-api-python-client",
    "google-auth-httplib2",
    "PyJWT",
    "requests",
)

# Service account credentials for Google Calendar access
# The calendar (techtomlet@gmail.com) must be shared with this service account
SERVICE_ACCOUNT_JSON = json.dumps({
    "type": "service_account",
    "project_id": "automation-reminder-481818",
    "private_key_id": "fa6c5ede3612bc5d7b38b9700a89146349be37cc",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCym+j4eJ4xWJWO\nTNZPg0RNtfWQURj6mrzM8EyPoLVS5y8A7Gl2RPgrRvQJunchIxO2GW4os5SabZpP\nrTxR7EZVRoKI6mNPeb9jO6eUG7HhDtk2BrPVJAyczuLzwuzj7dlRFM+gXbtRcZF7\n+nn/T+VfxAi7qHZipX24iwWDrNZtoB4s+2M99UYDSD7d776Tl1boGVolmXFBz8PA\n5qdYMSiZtqjXt6waxR4p9LfiUcg25pF4yVcckOgGrN4slQ/oC5dMgnFPTMHRSBXg\n7WlwLRs74hpHyq/4xiqTyOx8reKGhq6hDM+6LCoWAU8FXNfnGmmhyQ7rIyeRSDzT\nVzd5dKA9AgMBAAECggEADTyiym9eAfg3tUEajPAEiuHWXii0ejYnkeSpN+fIKGm7\nwQzEUCCSZ9qtUV9BXvJTjqZZ1KhidgNzcT48fzHMkJtWJ0F/tK8oMPmF1OMsjqpk\nDK34e+5dBO4MQdaLaeUBuxGYxaDMth99kbuhePt521wS7Z1xkKQFKj0bXoPbrGoW\nnAduiSE7wYBmS284nh47alfvBYeT6uH0q4MWsWFJo6hs8/b2M10BaaSU5VYItzjZ\nBOUJqJJctROj2RxrvaVp8e7E1xIVGA+xX4zgP8SPBb/IlSiGg3buYfiX6qzLMN2C\nuwHu07u/mkaUL3vRcJbsHWYAfD1OtS4oOAq9ViNeHQKBgQDrGK52UHLvB1OTRf3j\nGaZVKkltpuw7ZzUeVBPUvf6vs1LIzcQpWA28MJc9v7D73jsNWc0e28D8ay/QucaX\naJPuXFDFbYcRbEz4qcfwytAMYcH1nVwkfOHgD9rlmwIfWR/CARCJNt4dNWEPzT/C\nLgNHUyWEBKtsmkppMVvWLqbQnwKBgQDCfXMbzsr6BbLL9vL2IN+wziITUNedxMo2\nPY7EPb/VJA3uCdms6NAdQxpno6jcF6bq94EeZPfpG2QgObXPuaX1ZgKdm050xlfA\nOgg6rkf8cOEI8dg9lTh5D6iQfIpn2nTOw+WetcStUU4NP88HeHO0LzgUCEOa/5cG\nshzUTmdVowKBgQDBn9pQZ4HBi+8xZHvuBroPenxvawM1CZOeHvEWTkTswGx2JcJh\nqrvlOr/Vg4NobWeFX2io+aTAQCdpaRg+q0rrDe0YLVUI7IGYa3zYvLENAZaVi7zP\n8Gq391b5s+jTmLunNOlBmYbl14jRUuIoM21P2RMU4COvloOij5xrkpChUQKBgCle\nbcGYduw/kgx4dq2LyIjfD7h0FajlVu26okdzqv43MQ9U4Qw6aSoQP+mTkjNehI6u\nHrTMXT8kKGQCYn3Qy1ArZpsHkeSc28VzkpSIxZ8Yk4VHi+ttdhmqDvzMwNPeT8I7\nQPhFSZRkGuoOjIbWRCYrdQ4tw9OQUhuGf0NZeflpAoGASR/nCAjHmDd6YkKEfgxy\nj2/5TTF0/FqL9GE8xivBHyoULRYwMycZLs8srJ4tYQ6NdEtKAZXRqB4Ose47oAFv\nAy6JgIsvaoqFSYQSRpLHRwILN+tRi3m+io5fOLbCmCAM521br+P/qHuQSto9avsd\nc7jR4EikUQ10uEt2B2TbCKw=\n-----END PRIVATE KEY-----\n",
    "client_email": "mark-496@automation-reminder-481818.iam.gserviceaccount.com",
    "client_id": "114650536455139699162",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mark-496%40automation-reminder-481818.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})

CALENDAR_ID = "techtomlet@gmail.com"


def get_calendar_service():
    """Authenticate with Google Calendar using service account."""
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    creds_dict = json.loads(SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(
        creds_dict, scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )
    return build("calendar", "v3", credentials=creds)


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

web_app = FastAPI()


@web_app.get("/")
async def health():
    return {"status": "running", "service": "Airbnb Calendar - Check Availability"}


@web_app.post("/check-availability")
async def check_availability(request: Request):
    """Check if dates are available on the Google Calendar.

    Expects JSON: {"check_in": "YYYY-MM-DD", "check_out": "YYYY-MM-DD"}
    Returns: {"available": true/false, "message": "...", "conflicts": [...]}
    """
    try:
        body = await request.json()
        check_in = body.get("check_in")
        check_out = body.get("check_out")

        if not check_in or not check_out:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing check_in or check_out date. Format: YYYY-MM-DD"}
            )

        # Parse and validate dates
        try:
            ci_date = datetime.strptime(check_in, "%Y-%m-%d")
            co_date = datetime.strptime(check_out, "%Y-%m-%d")
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid date format. Use YYYY-MM-DD"}
            )

        if co_date <= ci_date:
            return JSONResponse(
                status_code=400,
                content={"error": "check_out must be after check_in"}
            )

        service = get_calendar_service()

        # Query events in the date range
        time_min = f"{check_in}T00:00:00Z"
        time_max = f"{check_out}T23:59:59Z"

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        # Filter for booking-type events (not just reminders)
        conflicts = []
        for event in events:
            summary = event.get("summary", "").lower()
            # Consider any event a potential booking conflict
            start = event["start"].get("date", event["start"].get("dateTime", ""))
            end = event["end"].get("date", event["end"].get("dateTime", ""))
            conflicts.append({
                "summary": event.get("summary", "Blocked"),
                "start": start,
                "end": end,
            })

        nights = (co_date - ci_date).days

        if conflicts:
            return {
                "available": False,
                "message": f"Those dates ({check_in} to {check_out}, {nights} nights) are not available. There are {len(conflicts)} existing booking(s) in that range.",
                "conflicts": conflicts,
                "check_in": check_in,
                "check_out": check_out,
                "nights": nights,
            }
        else:
            return {
                "available": True,
                "message": f"Great news! {check_in} to {check_out} ({nights} nights) is available.",
                "conflicts": [],
                "check_in": check_in,
                "check_out": check_out,
                "nights": nights,
            }

    except Exception as e:
        print(f"[CHECK-AVAILABILITY] Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.function(image=image)
@modal.asgi_app()
def check_availability_server():
    return web_app
