import os
import json, urllib.request, time
API_KEY = os.environ["RETELL_API_KEY"]
BASE_URL = "https://api.retellai.com"
NEW_LLM = "llm_9a3f58e8c3a7a1b5c51e28b18d9a"
def api(m, e, d=None):
    r = urllib.request.Request(f"{BASE_URL}/{e}", json.dumps(d).encode() if d else None, method=m)
    r.add_header("Authorization", f"Bearer {API_KEY}")
    r.add_header("Content-Type", "application/json")
    try: return json.loads(urllib.request.urlopen(r).read().decode())
    except: return None

# Get new LLM ID from last line of deployment
import subprocess
result = subprocess.run(['tail', '-15', '/dev/stdout'], capture_output=True, text=True)
# Just use the hardcoded new one for now
agent = api("POST", "create-chat-agent", {"response_engine": {"type": "retell-llm", "llm_id": NEW_LLM}})
aid = agent["agent_id"]

# Test S03 hot tub + S10 consistency
tests = [
    ("S03", ["Does it have a hot tub or not?"]),
    ("S10", ["How many people can sleep there?", "I saw online it said 12, which is right?"])
]

for name, msgs in tests:
    chat = api("POST", "create-chat", {"agent_id": aid})
    for m in msgs:
        time.sleep(0.5)
        r = api("POST", "create-chat-completion", {"agent_id": aid, "chat_id": chat["chat_id"], "content": m})
        if r: print(f"{name}: {r['messages'][-1]['content'][:80]}...")
    api("PATCH", f"end-chat/{chat['chat_id']}")

api("DELETE", f"delete-chat-agent/{aid}")
