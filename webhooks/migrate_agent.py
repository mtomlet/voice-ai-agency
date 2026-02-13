import json, requests

OLD_KEY = "key_442c3c70851f698c705fe75c2ab6"
NEW_KEY = "key_8970cab8ef7afa92828075dc1280"
H_OLD = {"Authorization": f"Bearer {OLD_KEY}", "Content-Type": "application/json"}
H_NEW = {"Authorization": f"Bearer {NEW_KEY}", "Content-Type": "application/json"}

WEBHOOK_URL = "https://techtomlet--lead-reactivation-webhooks-webhook-server.modal.run/post-call"

# 1. Get the LLM from old account
llm = requests.get("https://api.retellai.com/get-retell-llm/llm_d3834bebc87baf8d3a8443dbd085", headers=H_OLD).json()
print("Got LLM from old account")

# 2. Create LLM in new account
llm_payload = {
    "model": llm["model"],
    "general_prompt": llm["general_prompt"],
    "begin_message": llm["begin_message"],
    "general_tools": llm["general_tools"],
    "model_temperature": llm.get("model_temperature", 0.4),
}
resp = requests.post("https://api.retellai.com/create-retell-llm", headers=H_NEW, json=llm_payload)
new_llm = resp.json()
if resp.status_code != 201:
    print(f"LLM creation failed: {json.dumps(new_llm, indent=2)}")
    exit(1)
print(f"Created LLM: {new_llm['llm_id']}")

# 3. Get agent from old account
agent = requests.get("https://api.retellai.com/get-agent/agent_9a7131765c1e528371b83f93e6", headers=H_OLD).json()
print("Got Agent from old account")

# 4. Create agent in new account
agent_payload = {
    "agent_name": agent["agent_name"],
    "voice_id": agent["voice_id"],
    "language": agent.get("language", "en-US"),
    "response_engine": {
        "type": "retell-llm",
        "llm_id": new_llm["llm_id"]
    },
    "webhook_url": WEBHOOK_URL,
    "post_call_analysis_model": agent.get("post_call_analysis_model", "gpt-4.1-mini"),
    "post_call_analysis_data": agent.get("post_call_analysis_data", []),
    "ambient_sound": agent.get("ambient_sound", ""),
    "max_call_duration_ms": agent.get("max_call_duration_ms", 120000),
    "enable_voicemail_detection": agent.get("enable_voicemail_detection", True),
    "responsiveness": agent.get("responsiveness", 0.7),
    "interruption_sensitivity": agent.get("interruption_sensitivity", 0.6),
    "normalize_for_speech": agent.get("normalize_for_speech", True),
}
resp2 = requests.post("https://api.retellai.com/create-agent", headers=H_NEW, json=agent_payload)
new_agent = resp2.json()
if resp2.status_code != 201:
    print(f"Agent creation failed: {json.dumps(new_agent, indent=2)}")
    exit(1)
print(f"Created Agent: {new_agent['agent_id']}")

# 5. List phone numbers in new account
phones = requests.get("https://api.retellai.com/list-phone-numbers", headers=H_NEW).json()
print(f"\nPhone numbers in new account:")
for p in phones:
    print(f"  {p['phone_number_pretty']} ({p['phone_number']}) | outbound: {p.get('outbound_agent_id', 'none')}")

# 6. Assign agent to first available phone number
if phones:
    phone_num = phones[0]["phone_number"]
    assign = requests.patch(
        f"https://api.retellai.com/update-phone-number/{phone_num}",
        headers=H_NEW,
        json={
            "outbound_agent_id": new_agent["agent_id"],
            "nickname": "RE Lead Reactivation"
        }
    )
    if assign.status_code == 200:
        print(f"\nAssigned agent to {phone_num}")
    else:
        print(f"\nFailed to assign: {assign.text}")

print(f"\n=== RESULTS ===")
print(f"New LLM ID: {new_llm['llm_id']}")
print(f"New Agent ID: {new_agent['agent_id']}")
print(f"From Number: {phones[0]['phone_number'] if phones else 'NONE'}")
print(f"API Key: {NEW_KEY}")
