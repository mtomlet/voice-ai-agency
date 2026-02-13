# Lead Reactivation Voice Agent — Automation Build Prompt

> Paste everything below into a fresh Claude Code session. Claude will walk you through setup, build everything, and deploy it.

---

```
I need you to build the complete automation backend for a Real Estate Lead Reactivation Voice Agent. This system auto-dials old/cold leads from a Google Sheet, and after each call, writes the results back to the sheet. The voice agent itself is already configured in Retell AI — you are building the TWO WEBHOOKS that connect Retell to Google Sheets, plus an auto-dialer that calls one lead every 5 minutes.

Before we start, I need to give you some credentials. Ask me for each one, one at a time, and explain where to find it. Here's what you'll need:

## PLACEHOLDERS — Ask me for these:
1. RETELL_API_KEY — My Retell AI API key (found at retellai.com → Settings → API Keys)
2. RETELL_AGENT_ID — The agent ID of my Retell voice agent (found at retellai.com → Agents → click the agent → the ID in the URL or settings)
3. RETELL_FROM_NUMBER — The phone number in my Retell account to call FROM (found at retellai.com → Phone Numbers, must be E.164 format like +17575551234)
4. GOOGLE_SERVICE_ACCOUNT_JSON — The full JSON key file for a Google Cloud service account with Sheets API enabled. Walk me through creating this if I don't have one:
   - Go to console.cloud.google.com
   - Create a new project (or use existing)
   - Enable "Google Sheets API"
   - Go to IAM & Admin → Service Accounts → Create Service Account
   - Name it anything, click through, then click the account → Keys → Add Key → JSON
   - Download the JSON file
   - IMPORTANT: Copy the "client_email" from the JSON — I need to share my Google Sheet with this email (Editor access)
5. MODAL_TOKEN — My Modal.com token. Walk me through this if I don't have one:
   - Go to modal.com and create an account
   - Run `pip install modal` then `modal token new` in terminal
   - Or go to modal.com → Settings → API Tokens
6. GOOGLE_SHEET_ID — The ID from my Google Sheet URL (the long string between /d/ and /edit in the URL)

## STEP 1: CREATE THE GOOGLE SHEET CSV

First, create a CSV file called `lead-reactivation-sheet.csv` with exactly these columns and 10 sample leads. This is the template the client imports into Google Sheets.

COLUMNS (17 total):
first_name, last_name, phone_number, lead_source, original_interest, date_added, agent_name, transfer_number, call_status, interest_level, timeline, pre_approved, working_with_agent, transfer_attempted, notes, next_action, last_called

- Columns A-H are filled in by the client (lead info + agent info)
- Columns I-Q are filled in automatically by the post-call webhook after each call
- The "recording" column will be auto-created by the webhook after the first call

Generate 10 realistic sample leads with these specs:
- Phoenix/Scottsdale/Mesa/Gilbert/Chandler/Tempe area (Arizona real estate)
- Mix of buyers and sellers
- Various lead sources: Zillow, Realtor.com, Facebook Ad, Google Ad, Open House, Referral
- Various original interests: "3BR in Scottsdale under $500K", "Selling home in Mesa", "New construction in Gilbert", etc.
- agent_name for all: "Mike Thompson"
- transfer_number for all: "+16025551234" (placeholder)
- date_added: various dates in the past 3-12 months
- Columns I through Q should be EMPTY (these get filled by the AI after calling)
- phone_number format: +1XXXXXXXXXX (E.164 format)

IMPORTANT: Google Sheets stores phone numbers as integers and strips the + sign. The webhook code handles this — it extracts digits and re-adds the + prefix.

After creating the CSV, tell me:
"Import this CSV into Google Sheets (File → Import → Upload). Then share the sheet with your service account email (the client_email from your JSON key) as an Editor. Give me the Sheet ID from the URL."

## STEP 2: BUILD THE MODAL WEBHOOK SERVER

Create a file called `modal_app.py` that deploys to Modal.com. This is a FastAPI server with these endpoints:

### Architecture:
- Modal App name: "lead-reactivation-webhooks"
- Image: debian_slim with Python 3.11, pip_install: fastapi, gspread, google-auth, requests
- Web server: FastAPI wrapped in @modal.asgi_app() with min_containers=1 (always warm)
- Scheduled function: auto_dialer with modal.Cron("*/5 * * * *")

### Endpoint 1: GET /
Health check. Returns JSON with status and endpoint descriptions.

### Endpoint 2: POST /pre-call — Lead Context Lookup
This is the INBOUND webhook. Before each call, it looks up the lead by phone number.

How it works:
1. Receives JSON body with phone_number, from_number, or to_number
2. Normalizes the phone to last 10 digits (strips +1, country code, formatting)
3. Queries the Google Sheet for a matching row
4. Returns: first_name, last_name, phone_number, lead_source, original_interest, agent_name, transfer_number

Error handling:
- 400 if no phone number provided
- 404 if lead not found
- 500 on any exception

### Endpoint 3: POST /post-call — Update Google Sheet After Call
This is the POST-CALL webhook. Retell AI sends webhook events here after each call.

How it works:
1. Receives Retell webhook payload with event type and call data
2. If event is "call_started" → acknowledge and return (no action needed)
3. For call_ended and call_analyzed events:
   a. Extract call data from body.call
   b. Extract call_analysis from call.call_analysis
   c. Extract custom_analysis_data from call_analysis (this is where Retell puts post-call analysis variables)
   d. Get lead phone from call.to_number (outbound) or call.from_number (inbound), normalize to 10 digits
   e. Find the matching row in Google Sheet
   f. Build update values for columns I through Q:
      - call_status: from custom_data, or inferred (voicemail if call_analysis.in_voicemail, no_answer if disconnection_reason=="dial_no_answer", answered if transcript exists)
      - interest_level: from custom_data
      - timeline: from custom_data
      - pre_approved: from custom_data
      - working_with_agent: from custom_data
      - transfer_attempted: from custom_data
      - notes: from custom_data, fallback to call_analysis.call_summary
      - next_action: from custom_data
      - last_called: today's date (YYYY-MM-DD)
   g. Update each cell in the row using sheet.update_cell()
   h. RECORDING URL: Extract call.recording_url. If it exists:
      - Check if "recording" column header exists, if not create it
      - Write a HYPERLINK formula: =HYPERLINK("url", "▶ Play Recording")
      - This makes the recording playable in-browser when clicked in Google Sheets

### Endpoint 4: GET /next-call — Manual Trigger
Same as auto-dialer but triggered manually via browser/curl for testing.

### Function: auto_dialer — Runs Every 5 Minutes
Decorated with @app.function(image=image, schedule=modal.Cron("*/5 * * * *"))

Core logic (call_next_lead function):
1. Get all records from Google Sheet
2. Find the FIRST row where call_status is empty (uncalled lead)
3. If no uncalled leads remain → return {"status": "done"}
4. Format the phone number to E.164:
   - Extract digits only from the raw phone string
   - If 11 digits starting with "1" → "+{digits}" (already has country code)
   - If 10 digits → "+1{digits}" (add country code)
   - Otherwise → "+{digits}" (best effort)
5. Format the transfer_number the same way
6. Create outbound call via Retell API:
   POST https://api.retellai.com/v2/create-phone-call
   Headers: Authorization: Bearer {RETELL_API_KEY}, Content-Type: application/json
   Body:
   {
     "from_number": FROM_NUMBER,
     "to_number": formatted_phone,
     "override_agent_id": AGENT_ID,
     "retell_llm_dynamic_variables": {
       "first_name": lead.first_name,
       "last_name": lead.last_name,
       "phone_number": formatted_phone,
       "lead_source": lead.lead_source,
       "original_interest": lead.original_interest,
       "agent_name": lead.agent_name (default "Mike Thompson"),
       "transfer_number": formatted_transfer_number
     }
   }
7. Return result with call_id, name, phone, remaining count

### Google Sheets Authentication:
Use gspread + google.oauth2.service_account.Credentials
- Parse the service account JSON
- Scopes: ["https://www.googleapis.com/auth/spreadsheets"]
- Open sheet by key (GOOGLE_SHEET_ID)
- Get worksheet by name: "lead-reactivation-sheet"

### Phone Normalization Helper:
def normalize_phone(phone):
    Strip all non-digit characters, return last 10 digits.
    This handles +16025551234, 16025551234, (602) 555-1234, etc.

### IMPORTANT IMPLEMENTATION DETAILS:
- Embed the Google service account JSON directly in the Python file (Modal runs serverless, no filesystem)
- The sheet tab name MUST match exactly: "lead-reactivation-sheet" (this is the tab name, not the spreadsheet name)
- Google Sheets stores phone numbers as integers (strips the + prefix). The E.164 formatting logic handles this.
- gspread's update_cell uses USER_ENTERED input option by default, so =HYPERLINK() formulas will be parsed correctly
- Use min_containers=1 on the web server to keep it warm (no cold start delays for webhooks)

## STEP 3: DEPLOY TO MODAL

After building modal_app.py:
1. Make sure Modal CLI is installed: pip install modal
2. Set the Modal token if not already set
3. Deploy: modal deploy modal_app.py
4. Give me the deployment URL (will look like: https://USERNAME--lead-reactivation-webhooks-webhook-server.modal.run)

Then tell me:
"Your webhooks are live. Here's what to configure in Retell AI:
- Set your agent's Webhook URL to: {URL}/post-call
- The auto-dialer is running every 5 minutes and will call the next uncalled lead in your sheet.
- To pause the auto-dialer, I'll remove the cron schedule and redeploy.
- To test manually, hit {URL}/next-call in your browser."

## STEP 4: VERIFY EVERYTHING WORKS

After deployment:
1. Hit the health check endpoint (GET /) to confirm it's live
2. Offer to add my phone number as a test lead in the Google Sheet
3. Offer to trigger a test call via /next-call
4. Explain what should happen: the AI calls, has a conversation, then the post-call webhook fires and updates the Google Sheet row with call_status, interest_level, notes, recording link, etc.

## WHAT THIS SYSTEM DOES (for context):

This is a Real Estate Lead Reactivation system. Real estate agents spend thousands on leads (Zillow, Facebook ads, etc.) but only follow up with 2-3% of them. The rest sit in a spreadsheet, dead. This AI voice agent calls through those old leads automatically:

1. Agent uploads their old lead list to a Google Sheet
2. Every 5 minutes, the auto-dialer picks up the next uncalled lead
3. The AI calls them, references their original inquiry ("Hey Sarah, you had inquired about homes in Scottsdale...")
4. Qualifies them in under 2 minutes: timeline, pre-approval, working with another agent
5. HOT leads (under 6 months, no agent) → live-transferred to the agent's phone immediately
6. WARM leads → tagged for agent follow-up
7. COLD leads → tagged for nurture drip
8. Every call result is written back to the Google Sheet automatically
9. Recording links are embedded as clickable play buttons in the sheet

The voice agent prompt and Retell AI configuration are handled separately. This prompt ONLY builds the automation layer: the webhooks + auto-dialer + Google Sheets integration.
```

---

**Instructions:** Copy everything inside the code block above and paste it into a fresh Claude Code session. Claude will ask you for your API keys one at a time, build everything, and deploy it.
