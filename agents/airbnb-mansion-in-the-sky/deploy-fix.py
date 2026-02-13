#!/usr/bin/env python3
"""Deploy prompt fix — creates NEW LLM per caching bug workaround"""

import json
import urllib.request

API_KEY = "key_8970cab8ef7afa92828075dc1280"
BASE_URL = "https://api.retellai.com"

# Import the updated prompt from main script
import importlib.util
spec = importlib.util.spec_from_file_location("agent", "create-airbnb-agent.py")
mod = importlib.util.module_from_spec(spec)

# Read the file to extract SYSTEM_PROMPT and BEGIN_MESSAGE
with open("create-airbnb-agent.py") as f:
    content = f.read()

# Extract SYSTEM_PROMPT
start = content.index('SYSTEM_PROMPT = """') + len('SYSTEM_PROMPT = """')
end = content.index('"""', start)
SYSTEM_PROMPT = content[start:end]

# Extract BEGIN_MESSAGE
start = content.index('BEGIN_MESSAGE = "') + len('BEGIN_MESSAGE = "')
end = content.index('"', start)
BEGIN_MESSAGE = content[start:end]


def api_call(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            result = resp.read().decode()
            return json.loads(result) if result.strip() else {"status": "ok"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error {e.code}: {error_body}")
        raise


# Step 1: Create NEW LLM with fixed prompt
print("Creating NEW LLM with hallucination fix...")
llm = api_call("POST", "create-retell-llm", {
    "model": "gpt-4.1",
    "general_prompt": SYSTEM_PROMPT,
    "general_tools": [
        {
            "type": "end_call",
            "name": "end_call",
            "description": "End the call. Use when the conversation is complete, the caller says goodbye, or a hostile caller needs to be disconnected."
        },
        {
            "type": "transfer_call",
            "name": "transfer_to_owner",
            "description": "Transfer the call to the property owner. Use for: availability/booking questions, pricing/discount requests, maintenance issues during a stay, special requests, cancellations, payment/refund questions, or anything the agent doesn't know the answer to.",
            "transfer_destination": {
                "type": "predefined",
                "number": "{{transfer_number}}",
                "ignore_e164_validation": True
            },
            "transfer_option": {
                "type": "warm_transfer",
                "show_transferee_as_caller": False
            }
        }
    ],
    "begin_message": BEGIN_MESSAGE
})
llm_id = llm["llm_id"]
print(f"New LLM created: {llm_id}")

# Step 2: Create NEW agent pointing to new LLM
print("\nCreating NEW agent...")
agent = api_call("POST", "create-agent", {
    "agent_name": "Airbnb Concierge - Mansion In The Sky",
    "response_engine": {
        "type": "retell-llm",
        "llm_id": llm_id
    },
    "voice_id": "minimax-Nia",
    "voice_speed": 1.2,
    "language": "en-US",
    "opt_out_sensitive_data_storage": False,
    "enable_backchannel": True,
    "backchannel_frequency": 0.8,
    "backchannel_words": ["mm-hmm", "uh-huh"],
    "interruption_sensitivity": 0.8,
    "responsiveness": 1.0,
    "reminder_trigger_ms": 10000,
    "reminder_max_count": 2,
    "end_call_after_silence_ms": 60000,
    "max_call_duration_ms": 600000,
    "normalize_for_speech": True,
    "denoising_mode": "noise-and-background-speech-cancellation",
    "enable_voicemail_detection": True,
    "voicemail_message": "Hi, this is Alex calling from Mansion In The Sky on Beech Mountain. We got your call and wanted to follow up. Feel free to call us back anytime or check us out online at Carolina Cabin Rentals. Thanks!",
    "post_call_analysis_data": [
        {"type": "enum", "name": "caller_type", "description": "Type of caller", "choices": ["prospective_guest", "confirmed_guest", "current_guest", "other"]},
        {"type": "string", "name": "caller_name", "description": "Name of the caller if provided"},
        {"type": "string", "name": "questions_asked", "description": "Summary of questions the caller asked about the property"},
        {"type": "boolean", "name": "transferred_to_owner", "description": "Was the call transferred to the property owner?"},
        {"type": "string", "name": "transfer_reason", "description": "Why the call was transferred (if applicable)"},
        {"type": "boolean", "name": "interested_in_booking", "description": "Did the caller express interest in booking?"},
        {"type": "string", "name": "group_size", "description": "Number of guests mentioned by the caller"},
        {"type": "string", "name": "desired_dates", "description": "Dates mentioned by the caller (if any)"},
        {"type": "enum", "name": "call_outcome", "description": "How the call ended", "choices": ["questions_answered", "transferred_to_owner", "not_interested", "will_book_online", "maintenance_reported", "hostile_disconnect"]},
        {"type": "string", "name": "maintenance_issue", "description": "Description of any maintenance or property issue reported"},
        {"type": "boolean", "name": "caller_satisfied", "description": "Did the caller seem satisfied with the interaction?"}
    ],
    "post_call_analysis_model": "gpt-4.1"
})
agent_id = agent["agent_id"]
print(f"New Agent created: {agent_id}")

# Step 3: Publish
print("\nPublishing agent...")
api_call("POST", f"publish-agent/{agent_id}", {
    "version_description": "Hallucination Fix"
})
print("Agent published!")

print(f"\n{'='*60}")
print(f"FIXED AGENT DEPLOYED")
print(f"{'='*60}")
print(f"New Agent ID:  {agent_id}")
print(f"New LLM ID:    {llm_id}")
print(f"Old Agent ID:  agent_d64f2d85203dad1180f906d1b1")
print(f"Old LLM ID:    llm_2c0f9eeb8d3d53363edd0c4b3c90")
print(f"{'='*60}")
