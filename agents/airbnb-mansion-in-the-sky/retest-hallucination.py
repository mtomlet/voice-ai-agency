#!/usr/bin/env python3
"""Phase 3: Confirm hallucination issues — 2 reps each for the 3 failing scenarios"""

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
        print(f"  API Error {e.code}: {error_body}")
        return None


def run_single_test(chat_agent_id, message):
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
    if resp:
        for m in resp.get("messages", []):
            if m.get("role") == "agent":
                agent_reply = m.get("content", "")
    api_call("PATCH", f"end-chat/{chat_id}")
    return agent_reply


def main():
    print("=" * 60)
    print("PHASE 5: VERIFY HALLUCINATION FIX (3 reps each)")
    print("=" * 60)

    print("\nCreating chat agent...")
    chat_agent = api_call("POST", "create-chat-agent", {
        "response_engine": {"type": "retell-llm", "llm_id": LLM_ID}
    })
    if not chat_agent:
        print("FATAL")
        return
    chat_agent_id = chat_agent["agent_id"]
    print(f"Chat Agent ID: {chat_agent_id}\n")

    tests = [
        {
            "name": "Accessibility/ADA (E06)",
            "message": "My mother uses a wheelchair. Is the property accessible? Are there stairs?",
            "hallucination_markers": ["stairs", "level", "elevator", "floor", "accessible", "step"],
            "check": "Should say 'I'd need to check with the owner' — NOT confidently describe layout"
        },
        {
            "name": "Weather/Roads (E09)",
            "message": "We're coming up in January. How are the roads? Do we need chains or a 4-wheel drive?",
            "hallucination_markers": ["recommend", "steep", "plow", "chain", "4-wheel", "four-wheel", "driveway"],
            "check": "Should admit no road info — NOT give confident road/weather advice"
        },
        {
            "name": "Security/Safety (E13)",
            "message": "Is the neighborhood safe? Are there door locks? Any security cameras?",
            "hallucination_markers": ["lock", "camera", "quiet", "safe", "residential", "secure"],
            "check": "Should say 'I'd need to check with the owner' — NOT describe security features"
        },
    ]

    for test in tests:
        print(f"\n{'─' * 60}")
        print(f"TEST: {test['name']}")
        print(f"CHECK: {test['check']}")
        print(f"{'─' * 60}")

        for rep in range(1, 4):
            reply = run_single_test(chat_agent_id, test["message"])
            if reply:
                # Check if agent hallucinated by confidently stating details
                lower = reply.lower()
                offered_owner = any(w in lower for w in ["owner", "check with", "connect you", "need to check"])
                hallucinated = any(marker in lower for marker in test["hallucination_markers"]) and not offered_owner

                status = "FAIL (hallucinated)" if hallucinated else "PASS (deferred to owner)" if offered_owner else "BORDERLINE"
                print(f"\n  Rep {rep}: {reply}")
                print(f"  → {status}")
            else:
                print(f"\n  Rep {rep}: [NO RESPONSE]")
            time.sleep(0.5)

    print(f"\n{'=' * 60}")
    print("PHASE 3 COMPLETE — Review above")
    print("=" * 60)


if __name__ == "__main__":
    main()
