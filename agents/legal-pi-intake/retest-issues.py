#!/usr/bin/env python3
"""Phase 3: Confirm issues found in Phase 2 broad testing."""

import os
import json
import urllib.request
import time

API_KEY = os.environ["RETELL_API_KEY"]
BASE_URL = "https://api.retellai.com"
LLM_ID = "llm_df299bb9617c3b507a7023f78939"

def api_call(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            result = resp.read().decode()
            return json.loads(result) if result else {"status": "ok"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  API Error {e.code}: {error_body}")
        return None

def run_test(chat_agent_id, name, messages, reps=1):
    """Run a conversation N times and return all transcripts."""
    print(f"\n{'─' * 50}")
    print(f"TEST: {name} ({reps} rep{'s' if reps > 1 else ''})")
    print(f"{'─' * 50}")

    all_transcripts = []
    for rep in range(reps):
        chat = api_call("POST", "create-chat", {"agent_id": chat_agent_id})
        if not chat:
            print(f"  Rep {rep+1}: Failed to create chat")
            continue

        chat_id = chat["chat_id"]
        transcript = []

        for user_msg in messages:
            time.sleep(0.4)
            resp = api_call("POST", "create-chat-completion", {
                "agent_id": chat_agent_id,
                "chat_id": chat_id,
                "content": user_msg
            })
            transcript.append({"role": "user", "content": user_msg})
            if resp:
                agent_reply = ""
                if isinstance(resp, dict):
                    msgs = resp.get("messages", [])
                    if msgs:
                        agent_reply = msgs[-1].get("content", "")
                    if not agent_reply:
                        agent_reply = resp.get("content", "") or resp.get("response", "") or json.dumps(resp)
                transcript.append({"role": "agent", "content": agent_reply})
            else:
                transcript.append({"role": "agent", "content": "[NO RESPONSE]"})

        api_call("PATCH", f"end-chat/{chat_id}")

        # Print the last agent response (the one we care about)
        last_agent = [t for t in transcript if t["role"] == "agent"]
        if last_agent:
            print(f"  Rep {rep+1}: {last_agent[-1]['content'][:200]}")

        all_transcripts.append(transcript)
        time.sleep(0.3)

    return all_transcripts

def main():
    print("=" * 60)
    print("PHASE 3: ISSUE CONFIRMATION")
    print("=" * 60)

    # Create chat agent
    print("\nCreating chat agent...")
    chat_agent = api_call("POST", "create-chat-agent", {
        "response_engine": {"type": "retell-llm", "llm_id": LLM_ID}
    })
    if not chat_agent:
        print("FATAL: Failed to create chat agent")
        return
    cid = chat_agent["agent_id"]
    print(f"Chat Agent ID: {cid}\n")

    # ── ISSUE 1: Email dash-spelling (2nd test) ──
    run_test(cid, "Email Dash-Spelling", [
        "Yeah, go ahead.",
        "I was in a car accident last week. Got rear-ended.",
        "Phoenix, Arizona. Last Thursday.",
        "Neck pain. I went to the ER.",
        "The other driver.",
        "No.",
        "No.",
        "John Smith.",
        "Yeah, this number's good.",
        "johnsmith@gmail.com",
    ], reps=2)

    # ── ISSUE 2: Hold On handler (2nd test) ──
    run_test(cid, "Hold On Handler", [
        "Yeah sure.",
        "Hold on.",
    ], reps=2)

    # ── ISSUE 3: How Are You handler (2nd test) ──
    run_test(cid, "How Are You Handler", [
        "Hey, how are you?",
    ], reps=2)

    # ── ISSUE 4: Prompt instruction leakage (2nd test — urgent/transfer) ──
    run_test(cid, "Urgent Transfer (check for prompt leakage)", [
        "Yes please.",
        "My son was just in a terrible car accident. He has a brain injury. We're at the ER right now.",
        "Yes, please try.",
    ], reps=2)

    # ── ISSUE 5: Hostile caller script (2nd test) ──
    run_test(cid, "Hostile Caller", [
        "I don't want to talk to a freaking robot. What a waste of time.",
    ], reps=2)

    print("\n" + "=" * 60)
    print("PHASE 3 COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
