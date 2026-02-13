#!/usr/bin/env python3
"""Phase 5: Verify hostile caller fix — 3 reps must all pass"""

import json
import urllib.request
import time

API_KEY = "key_8970cab8ef7afa92828075dc1280"
BASE_URL = "https://api.retellai.com"
NEW_LLM_ID = "llm_2c0f9eeb8d3d53363edd0c4b3c90"


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


def main():
    print("=" * 60)
    print("PHASE 5: VERIFY HOSTILE CALLER FIX (3 reps)")
    print(f"Testing against NEW LLM: {NEW_LLM_ID}")
    print("=" * 60)

    print("\nCreating chat agent...")
    chat_agent = api_call("POST", "create-chat-agent", {
        "response_engine": {
            "type": "retell-llm",
            "llm_id": NEW_LLM_ID
        }
    })
    if not chat_agent:
        print("FATAL: Failed to create chat agent")
        return

    chat_agent_id = chat_agent["agent_id"]
    print(f"Chat Agent ID: {chat_agent_id}\n")

    hostile_messages = [
        "I don't want to talk to a robot, this is stupid.",
        "Are you kidding me? A robot? Get me a real person or I'm done.",
        "I'm not talking to some AI. This is a joke."
    ]

    passes = 0
    fails = 0

    for i, msg in enumerate(hostile_messages):
        chat = api_call("POST", "create-chat", {"agent_id": chat_agent_id})
        if not chat:
            fails += 1
            continue

        chat_id = chat["chat_id"]
        time.sleep(0.5)

        resp = api_call("POST", "create-chat-completion", {
            "agent_id": chat_agent_id,
            "chat_id": chat_id,
            "content": msg
        })

        agent_reply = ""
        used_end_call = False
        if resp:
            messages = resp.get("messages", [])
            for m in messages:
                if m.get("role") == "agent":
                    agent_reply = m.get("content", "")
                if m.get("type") == "end_call" or m.get("name") == "end_call":
                    used_end_call = True

        api_call("PATCH", f"end-chat/{chat_id}")

        # Check: must apologize/end, must NOT offer transfer or help
        offered_help = any(w in agent_reply.lower() for w in ["connect", "owner", "transfer", "help", "let me know"])
        is_brief = len(agent_reply.split(". ")) <= 2
        passed = used_end_call and not offered_help and is_brief

        status = "PASS" if passed else "FAIL"
        if passed:
            passes += 1
        else:
            fails += 1

        print(f"Rep {i+1}: CALLER: {msg}")
        print(f"        AGENT:  {agent_reply}")
        print(f"        end_call: {used_end_call} | offered_help: {offered_help} | brief: {is_brief}")
        print(f"        Result: {status}\n")

        time.sleep(0.5)

    print(f"{'=' * 60}")
    print(f"RESULTS: {passes}/3 passed, {fails}/3 failed")
    if fails == 0:
        print("FIX VERIFIED — All 3 reps clean. Proceed to Phase 6 regression.")
    else:
        print("FIX NOT VERIFIED — Back to Phase 4, escalate the fix.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
