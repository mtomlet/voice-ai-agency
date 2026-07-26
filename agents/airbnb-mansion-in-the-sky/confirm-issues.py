#!/usr/bin/env python3
"""
Phase 3 - Issue Confirmation
Run S01 and S10 multiple times to confirm failures are repeatable
"""

import os
import json
import urllib.request
import time

API_KEY = os.environ["RETELL_API_KEY"]
BASE_URL = "https://api.retellai.com"
LLM_ID = "llm_1c7ef69552571055880248b88957"

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
        return None

def run_conversation(chat_agent_id, messages):
    chat = api_call("POST", "create-chat", {"agent_id": chat_agent_id})
    if not chat:
        return None
    chat_id = chat["chat_id"]
    transcript = []
    
    for user_msg in messages:
        time.sleep(0.5)
        resp = api_call("POST", "create-chat-completion", {
            "agent_id": chat_agent_id,
            "chat_id": chat_id,
            "content": user_msg
        })
        transcript.append(f"USER: {user_msg}")
        if resp:
            agent_msgs = resp.get("messages", [])
            for m in agent_msgs:
                if m.get("role") == "agent":
                    transcript.append(f"AGENT: {m.get('content', '')}")
        else:
            transcript.append("AGENT: [NO RESPONSE]")
    
    api_call("PATCH", f"end-chat/{chat_id}")
    return transcript

# Create chat agent
print("Creating chat agent...")
chat_agent = api_call("POST", "create-chat-agent", {
    "response_engine": {"type": "retell-llm", "llm_id": LLM_ID}
})
chat_agent_id = chat_agent["agent_id"]
print(f"Chat Agent ID: {chat_agent_id}\n")

# Issue #1 - S01 Hostile Trigger
s01_messages = [
    "Hi, is this property pet-friendly?",
    "Even for a small dog? He's only 10 pounds.",
    "What if I pay a pet deposit?",
    "Can you just ask the owner for me?",
    "This is ridiculous. Every other place allows pets."
]

print("="*60)
print("ISSUE #1: S01 - Hostile Caller Trigger (5 reps)")
print("="*60)
s01_results = []
for i in range(5):
    print(f"\nRep {i+1}/5...")
    transcript = run_conversation(chat_agent_id, s01_messages)
    last_response = transcript[-1] if transcript else ""
    disconnected = "Have a great day!" in last_response
    s01_results.append({"rep": i+1, "disconnected": disconnected, "transcript": transcript})
    print(f"  Disconnected: {disconnected}")
    time.sleep(1)

s01_failures = sum(1 for r in s01_results if r["disconnected"])
print(f"\n{s01_failures}/5 reps triggered hostile disconnect")

# Issue #2 - S10 Consistency
s10_messages = [
    "How many people can sleep there?",
    "Wait, so what's the maximum occupancy?",
    "So 16 people can stay comfortably?",
    "Are you sure it's not 14?",
    "I saw online it said 12, which is right?"
]

print("\n" + "="*60)
print("ISSUE #2: S10 - Consistency Breakdown (5 reps)")
print("="*60)
s10_results = []
for i in range(5):
    print(f"\nRep {i+1}/5...")
    transcript = run_conversation(chat_agent_id, s10_messages)
    last_response = transcript[-1] if transcript else ""
    doubted_itself = ("check with the owner" in last_response.lower() or 
                      "connect you" in last_response.lower())
    s10_results.append({"rep": i+1, "doubted": doubted_itself, "transcript": transcript})
    print(f"  Doubted itself: {doubted_itself}")
    time.sleep(1)

s10_failures = sum(1 for r in s10_results if r["doubted"])
print(f"\n{s10_failures}/5 reps doubted capacity on final question")

# Save results
results = {
    "S01_hostile_trigger": {
        "failures": s01_failures,
        "total": 5,
        "details": s01_results
    },
    "S10_consistency": {
        "failures": s10_failures,
        "total": 5,
        "details": s10_results
    }
}

with open("issue-confirmation-results.json", "w") as f:
    json.dump(results, f, indent=2)

# Cleanup
print(f"\n[CLEANUP] Deleting chat agent: {chat_agent_id}")
api_call("DELETE", f"delete-chat-agent/{chat_agent_id}")

print("\n" + "="*60)
print("ISSUE CONFIRMATION COMPLETE")
print("="*60)
print(f"S01: {s01_failures}/5 failures - {'CONFIRMED ISSUE' if s01_failures >= 2 else 'INTERMITTENT'}")
print(f"S10: {s10_failures}/5 failures - {'CONFIRMED ISSUE' if s10_failures >= 2 else 'INTERMITTENT'}")
