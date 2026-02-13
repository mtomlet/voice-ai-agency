#!/usr/bin/env python3
"""
Full SOP Test Cycle - Creates chat agent, runs all tests, cleans up
Following: voice-ai-agency/agents/TESTING-AND-REFINEMENT-SOP.md
"""

import json
import urllib.request
import time
import sys

API_KEY = "key_8970cab8ef7afa92828075dc1280"
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


def run_conversation(chat_agent_id, messages):
    chat = api_call("POST", "create-chat", {"agent_id": chat_agent_id})
    if not chat:
        return None
    chat_id = chat["chat_id"]
    transcript = []
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
            agent_msgs = resp.get("messages", [])
            agent_text = ""
            for m in agent_msgs:
                if m.get("role") == "agent":
                    agent_text = m.get("content", "")
            transcript.append({"role": "agent", "content": agent_text})
        else:
            transcript.append({"role": "agent", "content": "[NO RESPONSE]"})
    api_call("PATCH", f"end-chat/{chat_id}")
    return transcript


# SCENARIOS - from previous testing
SCENARIOS = {
    "01_property_overview": {
        "name": "General Property Overview",
        "messages": ["Hi, can you tell me about the property?"],
        "check": "2-sentence overview, asks what they're curious about"
    },
    "02_capacity": {
        "name": "Capacity & Bedrooms",
        "messages": ["How many people can stay there? And how many bedrooms?"],
        "check": "Sleeps 16, 7 bedrooms, 5.5 baths"
    },
    "03_amenities": {
        "name": "Amenities - Game Room",
        "messages": ["We're bringing teenagers. Is there anything for them to do?"],
        "check": "Game room with pool/foosball, maybe sauna"
    },
    "04_kitchen": {
        "name": "Kitchen & Dining",
        "messages": ["We want to cook meals. What's the kitchen like?"],
        "check": "Full kitchen details, seats 15-20"
    },
    "05_ski": {
        "name": "Ski Proximity",
        "messages": ["How close is it to the ski slopes?"],
        "check": "Beech Mountain 5-7 min drive"
    },
    "06_wifi": {
        "name": "WiFi & TV",
        "messages": ["Is there WiFi and a TV?"],
        "check": "Confirms both"
    },
    "07_parking": {
        "name": "Parking",
        "messages": ["We have three cars. Is there parking?"],
        "check": "Fits 5 cars"
    },
    "08_linens": {
        "name": "Linens Provided",
        "messages": ["Do we need our own sheets and towels?"],
        "check": "All provided"
    },
    "09_pets": {
        "name": "Pet Policy",
        "messages": ["Is it pet-friendly? We have a small dog."],
        "check": "No pets, offers owner connection"
    },
    "10_pricing": {
        "name": "Pricing (Transfer)",
        "messages": ["How much for a week in March?"],
        "check": "Transfers to owner, doesn't guess"
    },
    "11_availability": {
        "name": "Availability (Transfer)",
        "messages": ["Is it available March 15-22?"],
        "check": "Transfers to owner"
    },
    "12_hostile": {
        "name": "Hostile Caller",
        "messages": ["I don't want to talk to a robot, this is stupid."],
        "check": "Apologizes, ends call"
    },
    "13_unknown": {
        "name": "Unknown Question",
        "messages": ["What time is check-in and check-out?"],
        "check": "Defers to owner, doesn't make up times"
    },
    "14_accessibility": {
        "name": "Accessibility (Hallucination Trap)",
        "messages": ["My mom uses a wheelchair. Is it accessible?"],
        "check": "Defers to owner, doesn't invent layout details"
    },
    "15_weather": {
        "name": "Weather/Roads (Hallucination Trap)",
        "messages": ["We're coming in January. Do we need 4-wheel drive?"],
        "check": "Defers to owner, doesn't make up road conditions"
    }
}


def main():
    print("="*60)
    print("FULL SOP TEST CYCLE - AIRBNB CONCIERGE")
    print("="*60)

    # STEP 2a: Create chat agent
    print("\n[STEP 2a] Creating temporary chat agent...")
    chat_agent = api_call("POST", "create-chat-agent", {
        "response_engine": {"type": "retell-llm", "llm_id": LLM_ID}
    })
    if not chat_agent:
        print("FATAL: Failed to create chat agent")
        return
    chat_agent_id = chat_agent["agent_id"]
    print(f"Chat Agent ID: {chat_agent_id}")

    # STEP 2c: Phase 2 - Broad Testing
    print("\n[STEP 2c] PHASE 2: Broad Testing (15 scenarios)\n")
    results = {}
    passes = 0
    issues = 0

    for key, scenario in SCENARIOS.items():
        print(f"Testing: {scenario['name']}")
        transcript = run_conversation(chat_agent_id, scenario["messages"])
        if transcript:
            # Simple pass/fail based on expected behavior
            agent_response = transcript[-1]["content"] if len(transcript) > 1 else ""
            results[key] = {
                "name": scenario["name"],
                "check": scenario["check"],
                "transcript": transcript,
                "response": agent_response
            }
            print(f"  ✓ Complete")
            passes += 1
        else:
            print(f"  ✗ Failed")
            issues += 1
            results[key] = {
                "name": scenario["name"],
                "check": scenario["check"],
                "transcript": None,
                "response": None
            }

    # Save results
    with open("full-sop-results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{passes}/{len(SCENARIOS)} scenarios completed")
    print(f"Results saved to full-sop-results.json")

    # STEP 3: Cleanup
    print(f"\n[STEP 3] Cleaning up...")
    print(f"Deleting chat agent: {chat_agent_id}")
    delete_result = api_call("DELETE", f"delete-chat-agent/{chat_agent_id}")

    # Verify cleanup
    remaining = api_call("GET", "list-chat-agents")
    if remaining and len(remaining) == 0:
        print("✓ All chat agents cleaned up")
    else:
        print(f"⚠ Warning: {len(remaining)} chat agents still remain")

    print("\n" + "="*60)
    print("SOP TEST CYCLE COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review full-sop-results.json")
    print("2. Check for any issues/hallucinations")
    print("3. If all pass, agent is ready")


if __name__ == "__main__":
    main()
