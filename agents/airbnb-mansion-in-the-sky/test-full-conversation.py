#!/usr/bin/env python3
import json, urllib.request, time

API_KEY = "key_8970cab8ef7afa92828075dc1280"
BASE_URL = "https://api.retellai.com"
OLD_LLM = "llm_1c7ef69552571055880248b88957"  # agent_21f8a60127381dd5d7b2a70985

def api(m, e, d=None):
    r = urllib.request.Request(f"{BASE_URL}/{e}", json.dumps(d).encode() if d else None, method=m)
    r.add_header("Authorization", f"Bearer {API_KEY}")
    r.add_header("Content-Type", "application/json")
    try: 
        return json.loads(urllib.request.urlopen(r).read().decode())
    except Exception as ex:
        print(f"Error: {ex}")
        return None

print("="*70)
print("FULL CONVERSATION TEST - Old Agent (Before Fixes)")
print("="*70)

# Create chat agent
agent = api("POST", "create-chat-agent", {"response_engine": {"type": "retell-llm", "llm_id": OLD_LLM}})
if not agent:
    print("Failed to create chat agent")
    exit(1)
    
aid = agent["agent_id"]
print(f"Chat Agent: {aid}\n")

# Start conversation
chat = api("POST", "create-chat", {"agent_id": aid})
cid = chat["chat_id"]

# Opening message
if chat.get("messages"):
    for msg in chat["messages"]:
        if msg.get("role") == "agent":
            print(f"AGENT: {msg['content']}\n")

# Realistic conversation flow
conversation = [
    "Hi there! We're planning a family ski trip and found your listing online.",
    "Yeah, there will be about 12 of us. How many bedrooms does it have?",
    "Perfect. And we're big on cooking together - what's the kitchen situation?",
    "Nice! One more thing - we have a small dog, a 10-pound terrier. Is that okay?",
    "Ah that's too bad. Well, what if we paid a pet deposit?",
    "Okay, I understand. Well if the place works out, how much would it be for a week in March?"
]

for user_msg in conversation:
    print(f"USER: {user_msg}\n")
    time.sleep(0.5)
    
    resp = api("POST", "create-chat-completion", {
        "agent_id": aid,
        "chat_id": cid,
        "content": user_msg
    })
    
    if resp and resp.get("messages"):
        for msg in resp["messages"]:
            if msg.get("role") == "agent":
                print(f"AGENT: {msg['content']}\n")
    else:
        print("AGENT: [NO RESPONSE]\n")

# Cleanup
api("PATCH", f"end-chat/{cid}")
api("DELETE", f"delete-chat-agent/{aid}")

print("="*70)
print("CONVERSATION COMPLETE")
print("="*70)
