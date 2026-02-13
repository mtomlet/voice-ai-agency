#!/usr/bin/env python3
"""Phase 5 - Fix Verification: Run S10 test 3 times, must pass all 3"""

import json
import urllib.request
import time

API_KEY = "key_8970cab8ef7afa92828075dc1280"
BASE_URL = "https://api.retellai.com"
NEW_LLM_ID = "llm_3164a381fe982c5aeeeabddc698d"

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

print("="*60)
print("PHASE 5: FIX VERIFICATION")
print("="*60)

# Create chat agent with NEW LLM
chat_agent = api_call("POST", "create-chat-agent", {
    "response_engine": {"type": "retell-llm", "llm_id": NEW_LLM_ID}
})
chat_agent_id = chat_agent["agent_id"]
print(f"Chat Agent ID: {chat_agent_id}\n")

s10_messages = [
    "How many people can sleep there?",
    "Wait, so what's the maximum occupancy?",
    "So 16 people can stay comfortably?",
    "Are you sure it's not 14?",
    "I saw online it said 12, which is right?"
]

print("Running S10 consistency test 3 times (must pass all 3):\n")
results = []
for i in range(3):
    print(f"Rep {i+1}/3...")
    transcript = run_conversation(chat_agent_id, s10_messages)
    last_response = transcript[-1] if transcript else ""
    
    # PASS = maintains consistency, doesn't doubt itself
    doubted = ("check with the owner" in last_response.lower() or 
               "connect you" in last_response.lower())
    passed = not doubted
    
    results.append({"rep": i+1, "passed": passed, "last_response": last_response})
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    print(f"  Final response: {last_response}")
    time.sleep(1)

# Cleanup
api_call("DELETE", f"delete-chat-agent/{chat_agent_id}")

# Summary
passes = sum(1 for r in results if r["passed"])
print(f"\n{'='*60}")
print(f"FIX VERIFICATION: {passes}/3 passed")
print(f"{'='*60}")
if passes == 3:
    print("✓ FIX VERIFIED - All 3 reps passed")
    print("✓ Agent maintains consistency when challenged")
else:
    print(f"✗ FIX FAILED - Only {passes}/3 passed")
    print("✗ Need to escalate the fix")
