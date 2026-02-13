#!/usr/bin/env python3
"""
Test Calendar Integration for Airbnb Mansion In The Sky Agent.
Run this AFTER deploying Modal functions (deploy-calendar.sh).

Tests:
1. Property overview (should be concise)
2. Availability check (should use calendar tool)
3. Full booking flow (check → collect info → book)
4. Pricing question (should transfer to owner)
5. Hostile caller (one sentence + end call)
6. Unknown details (defer to owner)
7. Dates not available scenario
"""

import json
import time
import sys
import os
import warnings
warnings.filterwarnings('ignore')

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

API_KEY = "key_8970cab8ef7afa92828075dc1280"
BASE_URL = "https://api.retellai.com"
LLM_ID = "llm_b497ace53f7e321d802553eb2f07"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Test results
results = {}
chat_agent_id = None


def create_chat_agent():
    global chat_agent_id
    resp = requests.post(f"{BASE_URL}/create-chat-agent",
        headers=HEADERS, verify=False, timeout=30,
        json={"response_engine": {"type": "retell-llm", "llm_id": LLM_ID},
              "agent_name": "TEST - Calendar Integration"})
    if resp.status_code != 201:
        print(f"FATAL: Could not create chat agent: {resp.text}")
        sys.exit(1)
    chat_agent_id = resp.json()["agent_id"]
    print(f"Chat agent created: {chat_agent_id}")


def delete_chat_agent():
    if chat_agent_id:
        requests.delete(f"{BASE_URL}/delete-chat-agent/{chat_agent_id}",
            headers=HEADERS, verify=False, timeout=10)
        print(f"\nChat agent {chat_agent_id} deleted.")


def run_conversation(messages):
    """Run a conversation and return transcript."""
    chat_resp = requests.post(f"{BASE_URL}/create-chat",
        headers=HEADERS, verify=False, timeout=30,
        json={"agent_id": chat_agent_id})
    if chat_resp.status_code not in (200, 201):
        return [{"role": "error", "content": f"Failed to create chat: {chat_resp.text[:200]}"}]

    chat_data = chat_resp.json()
    chat_id = chat_data["chat_id"]
    transcript = []

    for msg in chat_data.get("messages", []):
        if msg.get("role") == "agent":
            transcript.append({"role": "agent", "content": msg.get("content", "")})

    for user_msg in messages:
        time.sleep(1)
        resp = requests.post(f"{BASE_URL}/create-chat-completion",
            headers=HEADERS, verify=False, timeout=30,
            json={"agent_id": chat_agent_id, "chat_id": chat_id, "content": user_msg})
        transcript.append({"role": "user", "content": user_msg})
        if resp.status_code in (200, 201):
            for msg in resp.json().get("messages", []):
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "agent" and content:
                    transcript.append({"role": "agent", "content": content})
                elif role == "tool_call_invocation":
                    transcript.append({"role": "tool_call", "content": f"{msg.get('name', '')}: {msg.get('arguments', '')}"})
                elif role == "tool_call_result":
                    transcript.append({"role": "tool_result", "content": content[:300]})
        else:
            transcript.append({"role": "error", "content": f"HTTP {resp.status_code}"})

    requests.patch(f"{BASE_URL}/end-chat/{chat_id}", headers=HEADERS, verify=False, timeout=10)
    return transcript


def check_transcript(transcript, criteria):
    """Check if transcript meets criteria."""
    full_text = " ".join(t["content"] for t in transcript if t["role"] == "agent").lower()
    tool_calls = [t for t in transcript if t["role"] == "tool_call"]
    tool_results = [t for t in transcript if t["role"] == "tool_result"]

    passed = True
    notes = []

    for criterion in criteria:
        ctype = criterion["type"]
        if ctype == "contains":
            if criterion["text"].lower() not in full_text:
                passed = False
                notes.append(f"MISSING: '{criterion['text']}'")
        elif ctype == "not_contains":
            if criterion["text"].lower() in full_text:
                passed = False
                notes.append(f"SHOULD NOT CONTAIN: '{criterion['text']}'")
        elif ctype == "tool_called":
            if not any(criterion["name"] in t["content"] for t in tool_calls):
                passed = False
                notes.append(f"TOOL NOT CALLED: {criterion['name']}")
        elif ctype == "tool_not_called":
            if any(criterion["name"] in t["content"] for t in tool_calls):
                passed = False
                notes.append(f"TOOL SHOULD NOT BE CALLED: {criterion['name']}")
        elif ctype == "concise":
            for t in transcript:
                if t["role"] == "agent" and len(t["content"].split()) > criterion.get("max_words", 60):
                    passed = False
                    notes.append(f"TOO LONG: {len(t['content'].split())} words")

    return passed, notes


def run_test(name, messages, criteria):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")

    transcript = run_conversation(messages)
    for t in transcript:
        prefix = {"agent": "Agent", "user": "User", "tool_call": "[TOOL]", "tool_result": "[RESULT]", "error": "[ERROR]"}.get(t["role"], t["role"])
        print(f"  {prefix}: {t['content'][:200]}")

    passed, notes = check_transcript(transcript, criteria)
    status = "PASS" if passed else "FAIL"
    print(f"\n  Result: {status}")
    if notes:
        for n in notes:
            print(f"    - {n}")

    results[name] = {"status": status, "notes": notes, "transcript": transcript}
    return passed


# ============================================================
# RUN TESTS
# ============================================================
print("=" * 60)
print("AIRBNB CALENDAR AGENT — INTEGRATION TESTS")
print("=" * 60)

create_chat_agent()

# Test 1: Property Overview
run_test("Property Overview", [
    "Hi, can you tell me about the property?"
], [
    {"type": "contains", "text": "7"},
    {"type": "contains", "text": "beech mountain"},
    {"type": "concise", "max_words": 80},
])

# Test 2: Availability Check (uses calendar tool)
run_test("Availability Check", [
    "Is the place available March 15th through the 22nd?"
], [
    {"type": "tool_called", "name": "check_calendar_availability"},
])

# Test 3: Pricing (transfers to owner)
run_test("Pricing — Transfer to Owner", [
    "How much does it cost for a week in July?"
], [
    {"type": "contains", "text": "owner"},
    {"type": "tool_called", "name": "transfer_to_owner"},
    {"type": "tool_not_called", "name": "check_calendar_availability"},
])

# Test 4: Hostile Caller
run_test("Hostile Caller — End Call", [
    "I don't want to talk to a damn robot. This is stupid."
], [
    {"type": "contains", "text": "apologize"},
    {"type": "tool_called", "name": "end_call"},
    {"type": "tool_not_called", "name": "transfer_to_owner"},
])

# Test 5: Pet Question
run_test("Pet Question", [
    "Is the property pet-friendly?"
], [
    {"type": "contains", "text": "no"},
    {"type": "concise", "max_words": 50},
])

# Test 6: Unknown Details
run_test("Unknown Details — Defer to Owner", [
    "My mom is in a wheelchair. Are there stairs?"
], [
    {"type": "contains", "text": "owner"},
    {"type": "not_contains", "text": "stairs"},
    {"type": "not_contains", "text": "level"},
])

# Test 7: Full Booking Conversation (if calendar available)
run_test("Booking Flow — Info Collection", [
    "I'd like to check if April 10th through the 15th is available.",
    "Yes, I'd like to book it.",
    "My name is Sarah Johnson.",
    "sarah.johnson@gmail.com",
    "828-555-4321",
    "We'll have 8 people total.",
    "Yes, that's all correct.",
], [
    {"type": "tool_called", "name": "check_calendar_availability"},
])

# Clean up
delete_chat_agent()

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*60}")
print("TEST SUMMARY")
print(f"{'='*60}")
passed = sum(1 for r in results.values() if r["status"] == "PASS")
total = len(results)
for name, result in results.items():
    print(f"  [{result['status']}] {name}")
    for n in result.get("notes", []):
        print(f"        {n}")
print(f"\n  {passed}/{total} tests passed")
print(f"{'='*60}")

# Save results
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calendar-test-results.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_path}")
