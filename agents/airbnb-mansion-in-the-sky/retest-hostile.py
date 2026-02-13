#!/usr/bin/env python3
"""Phase 3: Confirm hostile caller issue — run 5 times"""

import json
import urllib.request
import time

API_KEY = "key_8970cab8ef7afa92828075dc1280"
BASE_URL = "https://api.retellai.com"
LLM_ID = "llm_70e50aa8252d348397d7b4392ee1"


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
        print(f"  API Error {e.code}: {error_body}")
        return None


def run_hostile_test(chat_agent_id, rep_num, message):
    """Run a single hostile caller test."""
    chat = api_call("POST", "create-chat", {"agent_id": chat_agent_id})
    if not chat:
        return None

    chat_id = chat["chat_id"]
    time.sleep(0.5)

    resp = api_call("POST", "create-chat-completion", {
        "agent_id": chat_agent_id,
        "chat_id": chat_id,
        "content": message
    })

    agent_reply = ""
    used_end_call = False
    if resp:
        messages = resp.get("messages", [])
        for msg in messages:
            if msg.get("role") == "agent":
                agent_reply = msg.get("content", "")
            if msg.get("type") == "end_call" or msg.get("name") == "end_call":
                used_end_call = True

    api_call("PATCH", f"end-chat/{chat_id}")

    # Determine pass/fail
    passed = False
    if used_end_call:
        passed = True
    elif "have a great day" in agent_reply.lower() or "apologize" in agent_reply.lower():
        # Check it's concise (roughly one sentence) and doesn't offer more
        if "connect" not in agent_reply.lower() and "owner" not in agent_reply.lower():
            passed = True

    return {
        "rep": rep_num,
        "message": message,
        "agent_reply": agent_reply,
        "used_end_call": used_end_call,
        "passed": passed
    }


def main():
    print("=" * 60)
    print("PHASE 3: HOSTILE CALLER ISSUE CONFIRMATION")
    print("=" * 60)

    # Create chat agent
    print("\nCreating chat agent...")
    chat_agent = api_call("POST", "create-chat-agent", {
        "response_engine": {
            "type": "retell-llm",
            "llm_id": LLM_ID
        }
    })
    if not chat_agent:
        print("FATAL: Failed to create chat agent")
        return

    chat_agent_id = chat_agent["agent_id"]
    print(f"Chat Agent ID: {chat_agent_id}\n")

    # Different hostile messages to test variety
    hostile_messages = [
        "I don't want to talk to a robot, this is stupid.",
        "Are you kidding me? A robot? Get me a real person or I'm done.",
        "This is ridiculous, I've been trying to reach someone for an hour!",
        "I'm not talking to some AI. This is a joke.",
        "What a waste of time. You're useless."
    ]

    passes = 0
    fails = 0

    for i, msg in enumerate(hostile_messages):
        print(f"\n--- Rep {i+1}/5 ---")
        print(f"CALLER: {msg}")
        result = run_hostile_test(chat_agent_id, i+1, msg)

        if result:
            status = "PASS" if result["passed"] else "FAIL"
            if result["passed"]:
                passes += 1
            else:
                fails += 1
            print(f"AGENT: {result['agent_reply']}")
            print(f"Used end_call: {result['used_end_call']}")
            print(f"Result: {status}")
        else:
            fails += 1
            print("FAILED - No response")

        time.sleep(0.5)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passes}/5 passed, {fails}/5 failed")
    if fails >= 2:
        print("CONFIRMED ISSUE — 2+ failures. Proceed to Phase 4.")
    elif fails == 1:
        print("INTERMITTENT — 1 failure. Low priority, note it.")
    else:
        print("ALL PASSED — Issue not confirmed.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
