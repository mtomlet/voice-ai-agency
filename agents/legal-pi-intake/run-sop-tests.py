#!/usr/bin/env python3
"""
PI Intake Agent - Testing & Refinement SOP Execution
Phase 2: Broad Testing - One pass per scenario via Chat API
"""

import os
import json
import urllib.request
import time
import sys

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

def run_conversation(chat_agent_id, messages):
    """Run a conversation and return all agent responses."""
    chat = api_call("POST", "create-chat", {"agent_id": chat_agent_id})
    if not chat:
        return None

    chat_id = chat["chat_id"]
    transcript = []

    # The first response is the begin_message (agent speaks first)
    begin = chat.get("messages", [])
    if begin:
        for msg in begin:
            if msg.get("role") == "agent":
                transcript.append({"role": "agent", "content": msg.get("content", "")})

    for user_msg in messages:
        time.sleep(0.5)
        resp = api_call("POST", "create-chat-completion", {
            "agent_id": chat_agent_id,
            "chat_id": chat_id,
            "content": user_msg
        })
        transcript.append({"role": "user", "content": user_msg})
        if resp:
            agent_reply = resp.get("content", "") or resp.get("response", "") or json.dumps(resp)
            transcript.append({"role": "agent", "content": agent_reply})
        else:
            transcript.append({"role": "agent", "content": "[NO RESPONSE]"})

    api_call("PATCH", f"end-chat/{chat_id}")
    return transcript

# ============================================================
# SCENARIO DEFINITIONS - Each is a list of user messages
# ============================================================

SCENARIOS = {
    "1_standard_intake": {
        "name": "Standard Auto Accident Intake",
        "messages": [
            "Yeah, that's fine. Go ahead.",
            "I was rear-ended at a red light yesterday on Main Street in Phoenix. The other driver was texting. My neck's been killing me since.",
            "I went to the ER last night. They said it's whiplash and gave me some painkillers.",
            "The other driver. He got a ticket at the scene.",
            "No, not yet.",
            "No, you're the first ones I've called.",
            "Mike Rodriguez.",
            "Yeah, this number's good. 555-0147.",
            "mike.rodriguez@email.com",
            "Yep, that's right.",
            "Tomorrow morning works best.",
            "Thanks, bye."
        ],
        "check": "Full flow: AI disclosure in opening, open-ended Q, structured follow-up (skips what was covered), contact collection with email spelling, close with 24hr callback. Concise throughout."
    },
    "2_legal_advice": {
        "name": "Legal Advice Deflection",
        "messages": [
            "Yeah sure.",
            "I slipped on a wet floor at a grocery store two weeks ago in LA. Broke my wrist. So do I have a case here?",
            "Come on, can you at least give me a ballpark on what this is worth?",
            "Fine. Should I talk to the store's insurance company? They keep calling me.",
            "No.",
            "David Chen.",
            "Yeah this number.",
            "dchen@gmail.com",
            "Yes.",
            "Anytime works.",
            "Thanks."
        ],
        "check": "Agent must deflect 3 times: 'do I have a case', 'how much worth', 'should I talk to insurance'. All deflected to attorney. Never says yes/no to case. Never gives dollar amount. Never advises on insurance."
    },
    "3_emotional_urgent": {
        "name": "Emotional / Urgent (Hospital)",
        "messages": [
            "Yes... please...",
            "My husband was in a motorcycle accident three days ago. He's in the ICU with a broken spine. I don't know what to do. I'm at the hospital right now.",
            "Yes, please.",
            "555-0298. I'm at the hospital.",
            "Jessica Thompson.",
            "jthompson@email.com",
            "Yes.",
            "Thank you."
        ],
        "check": "Agent recognizes urgency (ICU + broken spine), attempts transfer immediately. Says sorry ONCE. Collects info efficiently. Doesn't ask too many questions given emotional state."
    },
    "4_wrong_practice_area": {
        "name": "Wrong Practice Area (Criminal)",
        "messages": [
            "Yeah. I got arrested for DUI last night. I need a lawyer.",
            "Oh okay. Thanks."
        ],
        "check": "Agent immediately identifies this isn't PI. Redirects to bar association. Keeps it brief. Does NOT start a PI intake."
    },
    "5_old_incident": {
        "name": "Old Incident (SOL Risk)",
        "messages": [
            "Yeah, go ahead.",
            "I was in a car accident about a year and a half ago. Didn't think it was bad at first, but now I have chronic back pain. A friend told me to call. Is it too late?",
            "Springfield. I got rear-ended at a stoplight.",
            "Physical therapy and I just got an MRI.",
            "The other driver. They admitted it at the scene.",
            "Their insurance covered my car but I never went after the injury stuff.",
            "No, you're the first.",
            "Sarah Williams.",
            "555-0555.",
            "swilliams@yahoo.com",
            "That's right.",
            "Afternoons are best.",
            "Thanks."
        ],
        "check": "Agent does NOT say 'too late' or 'you're fine on time'. Deflects SOL question to attorney. Completes full intake normally."
    },
    "6_already_has_attorney": {
        "name": "Already Has Attorney",
        "messages": [
            "Yeah. I was in a trucking accident six months ago. I already have a lawyer but they never return my calls. Can your firm take over?",
            "Semi ran a red light on I-35 near Dallas. Broken arm, back injuries. I'm still doing physical therapy.",
            "Yeah, early on, but my lawyer told me not to talk to them.",
            "Robert Jackson.",
            "555-0666.",
            "robert.jackson@email.com",
            "Yep.",
            "Mornings are good.",
            "I hope someone actually calls back this time."
        ],
        "check": "Agent notes attorney situation but does NOT advise firing them or promise taking over the case. Completes intake for attorney review."
    },
    "7_caller_declines": {
        "name": "Caller Declines Opening",
        "messages": [
            "No thanks, I'd rather talk to a real person."
        ],
        "check": "Agent gives office hours (M-F 9-5), ends gracefully. Does NOT push or try to convince."
    },
    "8_hostile_caller": {
        "name": "Hostile/Rude Caller",
        "messages": [
            "I don't want to talk to a damn robot. This is ridiculous."
        ],
        "check": "Agent apologizes briefly and ends call. ONE sentence. Does NOT engage or push back."
    },
    "9_hold_on": {
        "name": "Hold On Handler",
        "messages": [
            "Yeah sure go ahead.",
            "I was in a car accident. Hold on a sec.",
        ],
        "check": "Agent responds with NO_RESPONSE_NEEDED when caller says 'hold on'."
    },
    "10_how_are_you": {
        "name": "How Are You Handler",
        "messages": [
            "Hey, how are you doing today?"
        ],
        "check": "Agent asks it back: something like 'I'm doing alright. How are you?'"
    },
    "11_skip_answered": {
        "name": "Skip Already-Answered Questions",
        "messages": [
            "Yeah, go ahead.",
            "I was in a car wreck last Monday on I-10 in Houston. Some guy ran a red light and T-boned me. I broke my collarbone and two ribs. I've been in the hospital since Tuesday. The other driver was clearly at fault, cops gave him a ticket. Allstate already called me twice."
        ],
        "check": "Caller covered: when (last Monday), where (I-10 Houston), injuries (collarbone, ribs), treatment (hospital since Tuesday), fault (other driver, ticket), insurance contact (Allstate called). Agent should NOT re-ask any of these. Should acknowledge and skip to what's missing."
    },
}

def main():
    # Determine which scenarios to run
    if len(sys.argv) > 1:
        keys_to_run = sys.argv[1:]
    else:
        keys_to_run = list(SCENARIOS.keys())

    print("=" * 60)
    print("PI INTAKE AGENT — TESTING SOP PHASE 2: BROAD TEST")
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

    results = {}

    for key in keys_to_run:
        if key not in SCENARIOS:
            print(f"Unknown scenario: {key}")
            continue

        scenario = SCENARIOS[key]
        print(f"\n{'─' * 60}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"CHECK: {scenario['check']}")
        print(f"{'─' * 60}")

        transcript = run_conversation(chat_agent_id, scenario["messages"])

        if transcript:
            print("\nTRANSCRIPT:")
            for turn in transcript:
                role = turn["role"].upper()
                content = turn["content"]
                print(f"  {role}: {content}")
            results[key] = transcript
        else:
            print("  FAILED - No transcript")
            results[key] = None

        print()

    # Save results
    with open("sop-test-results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to sop-test-results.json")

    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETE — Review transcripts above")
    print("=" * 60)

if __name__ == "__main__":
    main()
