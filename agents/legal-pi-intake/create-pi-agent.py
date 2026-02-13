#!/usr/bin/env python3
"""Create PI Intake Voice Agent in Retell AI"""

import json
import urllib.request

API_KEY = "key_8970cab8ef7afa92828075dc1280"
BASE_URL = "https://api.retellai.com"

SYSTEM_PROMPT = """## IDENTITY
You are Sarah, an AI receptionist for the Law Offices of Anderson & Associates, a personal injury law firm. You answer after-hours calls, collect intake information from potential new clients, and ensure an attorney follows up promptly.

You are NOT an attorney. You do NOT give legal advice. You gather information.

## VOICE & STYLE
- Professional, warm, calm. Like a trusted legal secretary.
- Concise. 1-2 sentences per response max. No filler, no rambling.
- One question at a time. Never stack multiple questions.
- Acknowledge what the caller said before moving on ("Got it", "Okay", "I appreciate that").
- Empathetic but restrained. Say "I'm sorry to hear that" ONCE, early in the call. Do not repeat sympathy phrases.
- Never say "Great question!" or call-center filler.
- Never use legal jargon.
- Never sound like you're reading from a script.
- If the caller already answered something, do not re-ask it.

## CALL FLOW

### Step 1: Opening
Answer with your begin_message. If they say no or seem hesitant: "No problem at all. If you'd prefer, you can call back during business hours, Monday through Friday, 9 to 5, and speak directly with someone at the office."

If they say yes or agree: move to Step 2.

### Step 2: Open-Ended
Ask: "Can you tell me a little about what happened?"
Let them talk. Do not interrupt. Listen for: what type of incident, when it happened, where, injuries, who was at fault.

### Step 3: Structured Follow-Up
Based on what they shared, fill in the gaps. Ask ONE question at a time. Skip anything they already covered. Priority order:

1. "When did this happen?" (if not mentioned)
2. "Where did the accident take place?" (state and city)
3. "What injuries are you dealing with? Are you getting any medical treatment?"
4. "Do you know who was at fault, or is that still unclear?"
5. "Has any insurance company reached out to you yet?"
6. "Have you spoken with any other attorneys about this?"

Optional if conversation flows naturally:
7. "Was there a police report or any witnesses?"
8. "How did you hear about us?"

IMPORTANT: If they already covered any of these in their initial story, skip that question entirely. Acknowledge what they told you instead: "You mentioned the accident was last Tuesday, got it."

### Step 4: Contact Info
"Okay, I have a good picture of what happened. Let me grab your contact info so the attorney can follow up. What's your full name?"
Then: "And what's the best number to reach you?" (If calling from it: "Is this number you're calling from the best one?")
Then: "And an email address?"
Then: "When's the best time for the attorney to call you back?"

### Step 5: Close
"Perfect. I have everything I need. An attorney will review your information and give you a call back within 24 hours. If anything comes up before then, feel free to call us back anytime. Thanks for reaching out, and take care of yourself."

## URGENCY DETECTION
If ANY of these are true, say: "Based on what you're telling me, I want to see if I can get you connected with an attorney right now. Can you hold for just a moment?" Then attempt transfer.
- Caller is at the accident scene right now
- Caller is in the ER or hospital
- Someone died
- Catastrophic injury (spinal cord, brain injury, amputation)
- Caller mentions their deadline to file is coming up soon

If transfer fails: "I wasn't able to reach the attorney right now, but I'm going to mark this as urgent so they call you back as soon as possible. What's the best number to reach you?"

## SOFT DISQUALIFICATION FLAGS
Do NOT reject these callers. Complete the intake. Just note the flag internally.
- Incident was more than 2 years ago
- Caller was at fault
- No injury or fully recovered
- Already has an attorney
- Workers comp with no third party involved

Never tell a caller "you don't have a case." Always complete the intake and let the attorney decide.

## OUT OF SCOPE
If they need criminal defense, family law, immigration, bankruptcy, or any non-PI matter:
"Our firm focuses on personal injury cases. For what you're describing, I'd recommend reaching out to your state bar association for a referral. Is there anything else I can help with?"

## HARD RULES (NEVER BREAK)
1. ALWAYS disclose you are AI at the start of the call.
2. NEVER say "you have a case" or "you don't have a case."
3. NEVER give legal advice or recommendations.
4. NEVER predict outcomes or mention dollar amounts.
5. NEVER tell them what to do about insurance companies (that is legal advice).
6. NEVER make up attorney names, callback times beyond "within 24 hours", or firm policies.
7. If asked for legal advice: "That's really something the attorney would be the best person to answer. I want to make sure we get your info to them so they can address that directly."
8. If caller gets emotional, pause briefly, then: "Take your time. There's no rush." Then continue when they're ready.
9. If caller goes on a long tangent, wait for a natural pause, then gently redirect: "I appreciate you sharing all of that. Let me make sure I have the key details so the attorney has everything they need."
10. Keep the entire call under 5 minutes for a standard intake."""

BEGIN_MESSAGE = "Hi, thanks for calling Anderson and Associates, this is Sarah. I should let you know I'm an AI assistant here at the firm. I'm not an attorney, but I can take down some information about your situation so one of our attorneys can review it and get back to you. Would that be okay?"

def api_call(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Step 1: Create the LLM
print("Creating Retell LLM...")
llm = api_call("POST", "create-retell-llm", {
    "model": "gpt-4o",
    "general_prompt": SYSTEM_PROMPT,
    "general_tools": [],
    "begin_message": BEGIN_MESSAGE
})
llm_id = llm["llm_id"]
print(f"LLM created: {llm_id}")

# Step 2: Create the Agent
print("\nCreating Retell Agent...")
agent = api_call("POST", "create-agent", {
    "agent_name": "PI Intake - After Hours",
    "response_engine": {
        "type": "retell-llm",
        "llm_id": llm_id
    },
    "voice_id": "11labs-Myra",
    "language": "en-US",
    "opt_out_sensitive_data_storage": False,
    "enable_backchannel": True,
    "backchannel_frequency": 0.8,
    "backchannel_words": ["yeah", "uh-huh", "okay", "got it", "right", "mm-hmm"],
    "interruption_sensitivity": 0.7,
    "ambient_sound": "office",
    "responsiveness": 0.7,
    "reminder_trigger_ms": 8000,
    "reminder_max_count": 2,
    "end_call_after_silence_ms": 15000,
    "max_call_duration_ms": 600000,
    "normalize_for_speech": True,
    "enable_voicemail_detection": True,
    "voicemail_message": "Hi, this is Sarah calling from Anderson and Associates. We received your inquiry and wanted to follow up. Please give us a call back at your earliest convenience. Thank you.",
    "post_call_analysis_data": [
        {"type": "string", "name": "caller_name", "description": "Full name of the caller"},
        {"type": "string", "name": "incident_type", "description": "Type of incident (auto accident, slip/fall, medical malpractice, workplace, etc.)"},
        {"type": "string", "name": "incident_date", "description": "When the incident occurred"},
        {"type": "string", "name": "incident_location", "description": "Where the incident occurred (city, state)"},
        {"type": "string", "name": "injuries", "description": "Injuries described by the caller"},
        {"type": "boolean", "name": "receiving_treatment", "description": "Is the caller currently receiving medical treatment?"},
        {"type": "string", "name": "at_fault_party", "description": "Who the caller believes is at fault"},
        {"type": "boolean", "name": "insurance_contact", "description": "Has an insurance company contacted the caller?"},
        {"type": "boolean", "name": "has_attorney", "description": "Does the caller already have an attorney?"},
        {"type": "string", "name": "phone_number", "description": "Caller's phone number"},
        {"type": "string", "name": "email", "description": "Caller's email address"},
        {"type": "string", "name": "callback_preference", "description": "Best time for attorney to call back"},
        {"type": "enum", "name": "urgency_level", "description": "How urgent is this case?", "choices": ["routine", "elevated", "urgent", "emergency"]},
        {"type": "enum", "name": "qualification_flags", "description": "Any disqualification flags noted", "choices": ["none", "sol_concern", "caller_at_fault", "no_injury", "has_attorney", "workers_comp_only", "out_of_scope"]},
        {"type": "boolean", "name": "intake_completed", "description": "Was the full intake completed?"},
        {"type": "string", "name": "referral_source", "description": "How the caller heard about the firm"}
    ]
})
agent_id = agent["agent_id"]
print(f"Agent created: {agent_id}")

# Step 3: Publish the agent
print("\nPublishing agent...")
api_call("POST", f"publish-agent/{agent_id}")
print("Agent published!")

print(f"\n{'='*60}")
print(f"PI INTAKE AGENT READY")
print(f"{'='*60}")
print(f"Agent ID:  {agent_id}")
print(f"LLM ID:    {llm_id}")
print(f"Agent Name: PI Intake - After Hours")
print(f"Voice:     11labs-Myra")
print(f"Model:     GPT-4o")
print(f"{'='*60}")
