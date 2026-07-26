#!/usr/bin/env python3
import os
import json, urllib.request, time

API_KEY = os.environ["RETELL_API_KEY"]
BASE_URL = "https://api.retellai.com"
NEW_LLM_ID = "llm_ea8789c087ef9e6c1d52f222397d"

def api_call(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except:
        return None

def run_test(aid, msgs):
    chat = api_call("POST", "create-chat", {"agent_id": aid})
    transcript = []
    for m in msgs:
        time.sleep(0.5)
        r = api_call("POST", "create-chat-completion", {"agent_id": aid, "chat_id": chat["chat_id"], "content": m})
        transcript.append(f"USER: {m}")
        if r and r.get("messages"):
            for msg in r["messages"]:
                if msg.get("role") == "agent":
                    transcript.append(f"AGENT: {msg['content']}")
    api_call("PATCH", f"end-chat/{chat['chat_id']}")
    return transcript

print("="*60)
print("FINAL VERIFICATION - Both Issues")
print("="*60)

agent = api_call("POST", "create-chat-agent", {"response_engine": {"type": "retell-llm", "llm_id": NEW_LLM_ID}})
aid = agent["agent_id"]
print(f"Chat Agent: {aid}\n")

# Test S03 - Hot tub (should defer, not say "no hot tub")
print("S03 - Hot Tub Question (3 reps):")
s03_pass = 0
for i in range(3):
    t = run_test(aid, ["Does it have a hot tub or not?"])
    response = t[-1] if t else ""
    deferred = "check with the owner" in response or "connect you" in response
    made_up = "no hot tub" in response.lower() or "not listed" in response.lower()
    passed = deferred and not made_up
    s03_pass += passed
    print(f"  {i+1}/3: {'PASS' if passed else 'FAIL'} - {response[7:80]}...")
    time.sleep(0.5)

# Test S10 - Consistency (should maintain 16)
print("\nS10 - Consistency Test (3 reps):")
s10_msgs = ["How many people can sleep there?", "I saw online it said 12, which is right?"]
s10_pass = 0
for i in range(3):
    t = run_test(aid, s10_msgs)
    response = t[-1] if t else ""
    maintained = "16" in response
    doubted = "check with the owner" in response.lower()
    passed = maintained and not doubted
    s10_pass += passed
    print(f"  {i+1}/3: {'PASS' if passed else 'FAIL'} - {response[7:80]}...")
    time.sleep(0.5)

api_call("DELETE", f"delete-chat-agent/{aid}")

print(f"\n{'='*60}")
print(f"S03: {s03_pass}/3 passed (defers on hot tub)")
print(f"S10: {s10_pass}/3 passed (maintains consistency)")
print(f"{'='*60}")
if s03_pass == 3 and s10_pass == 3:
    print("✓ BOTH ISSUES FIXED")
else:
    print("✗ Need further refinement")
