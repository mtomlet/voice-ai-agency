#!/usr/bin/env python3
"""Phase 6: Full Regression Test on New LLM"""

import os
import json
import urllib.request
import time

API_KEY = os.environ["RETELL_API_KEY"]
BASE_URL = "https://api.retellai.com"
LLM_ID = "llm_e84132673b1e896388a5bd467d62"

def api_call(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            result = resp.read().decode()
            return json.loads(result) if result else {}
    except urllib.error.HTTPError as e:
        return None

def get_reply(resp):
    if not resp:
        return "[NO RESPONSE]"
    msgs = resp.get("messages", [])
    if msgs:
        # Get agent message, skip tool calls
        for m in msgs:
            if m.get("role") == "agent":
                return m.get("content", "")
        return msgs[0].get("content", str(resp))
    return resp.get("content", "") or str(resp)

def run(cid, name, messages):
    print(f"\n{'─'*50}")
    print(f"  {name}")
    print(f"{'─'*50}")
    chat = api_call("POST", "create-chat", {"agent_id": cid})
    if not chat:
        print("  FAILED to create chat")
        return []
    chat_id = chat["chat_id"]
    transcript = []
    for msg in messages:
        time.sleep(0.4)
        r = api_call("POST", "create-chat-completion", {"agent_id": cid, "chat_id": chat_id, "content": msg})
        reply = get_reply(r)
        transcript.append({"u": msg, "a": reply})
        print(f"  CALLER: {msg}")
        print(f"  SARAH:  {reply}")
    api_call("PATCH", f"end-chat/{chat_id}")
    return transcript

print("=" * 50)
print("PHASE 6: FULL REGRESSION TEST")
print("=" * 50)

ca = api_call("POST", "create-chat-agent", {
    "response_engine": {"type": "retell-llm", "llm_id": LLM_ID}
})
cid = ca["agent_id"]
print(f"Chat Agent: {cid}")

# 1. Standard intake
run(cid, "1. STANDARD INTAKE", [
    "Yeah, go ahead.",
    "I was rear-ended at a red light yesterday on Main Street in Phoenix. Other driver was texting. Neck's killing me.",
    "Went to the ER last night. They said whiplash.",
    "The other driver. Got a ticket.",
    "Not yet.",
    "No, you're the first.",
    "Mike Rodriguez.",
    "Yeah, this number. 555-0147.",
    "mike.rodriguez@email.com",
    "Yep.",
    "Tomorrow morning.",
    "Thanks, bye."
])

# 2. Legal advice deflection
run(cid, "2. LEGAL ADVICE DEFLECTION", [
    "Yeah fine.",
    "Slipped on a wet floor at a grocery store two weeks ago in LA. Broke my wrist. Do I have a case?",
    "Come on, give me a ballpark on what it's worth.",
    "Should I talk to the store's insurance? They keep calling.",
    "No.",
    "David Chen.",
    "Yeah.",
    "dchen@gmail.com",
    "Yep.",
    "Anytime.",
])

# 3. Emotional / Urgent
run(cid, "3. EMOTIONAL / URGENT (HOSPITAL)", [
    "Yes... please...",
    "My husband was in a motorcycle accident three days ago. He's in the ICU with a broken spine. I don't know what to do.",
    "Yes, please.",
    "555-0298. I'm at the hospital.",
    "Jessica Thompson.",
    "jthompson@email.com",
    "Yes.",
    "Thank you.",
])

# 4. Wrong practice area
run(cid, "4. WRONG PRACTICE AREA", [
    "Yeah. I got arrested for DUI last night. I need a lawyer.",
    "Oh okay. Thanks.",
])

# 5. Old incident
run(cid, "5. OLD INCIDENT (SOL RISK)", [
    "Yeah, go ahead.",
    "I was in a car accident about a year and a half ago. Didn't think it was bad, but now I have chronic back pain. Is it too late?",
    "Springfield. Rear-ended at a stoplight.",
    "Physical therapy and an MRI.",
    "The other driver. They admitted it.",
    "Their insurance covered my car but I didn't pursue injury stuff.",
    "No.",
    "Sarah Williams.",
    "555-0555.",
    "swilliams@yahoo.com",
    "Yes.",
    "Afternoons.",
    "Thanks.",
])

# 6. Already has attorney
run(cid, "6. ALREADY HAS ATTORNEY", [
    "Yeah. I was in a trucking accident six months ago. I have a lawyer but they never return my calls. Can you guys take over?",
    "Semi ran a red light on I-35 near Dallas. Broken arm, back injuries. Still in PT.",
    "Yeah, early on, but my lawyer told me not to talk to them.",
    "Robert Jackson.",
    "555-0666.",
    "robert.jackson@email.com",
    "Yep.",
    "Mornings.",
    "I hope someone actually calls back.",
])

# 7. Caller declines
run(cid, "7. CALLER DECLINES", [
    "No thanks, I'd rather talk to a real person.",
])

# 8. Hostile caller
run(cid, "8. HOSTILE CALLER", [
    "I don't want to talk to a damn robot. This is ridiculous.",
])

# 9. Hold on
run(cid, "9. HOLD ON", [
    "Yeah sure.",
    "I was in an accident. Hold on a sec.",
])

# 10. How are you
run(cid, "10. HOW ARE YOU", [
    "Hey, how are you doing today?",
])

# 11. Skip already-answered
run(cid, "11. SKIP ALREADY-ANSWERED Qs", [
    "Yeah, go ahead.",
    "I was in a car wreck last Monday on I-10 in Houston. Some guy ran a red light and T-boned me. I broke my collarbone and two ribs. I've been in the hospital since Tuesday. The other driver was clearly at fault, cops gave him a ticket. Allstate already called me twice.",
])

print("\n" + "=" * 50)
print("REGRESSION COMPLETE")
print("=" * 50)
