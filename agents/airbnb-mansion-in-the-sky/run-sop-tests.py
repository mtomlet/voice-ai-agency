#!/usr/bin/env python3
"""
Airbnb Mansion In The Sky Agent - Testing & Refinement SOP Execution
Phase 2: Broad Testing - One pass per scenario via Chat API
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
# PHASE 1: SCENARIO INVENTORY
# Every distinct scenario from the prompt, explicit and implicit
# ============================================================

SCENARIOS = {
    "01_property_overview": {
        "name": "General Property Overview",
        "messages": [
            "Hi, can you tell me about the property?"
        ],
        "check": "Agent gives 2-sentence overview, then asks what specifically they want to know. Does NOT dump all amenities in one breath."
    },
    "02_capacity_bedrooms": {
        "name": "Capacity & Bedrooms Question",
        "messages": [
            "Hey, how many people can stay there? And how many bedrooms?"
        ],
        "check": "Agent answers directly: sleeps 16, 7 bedrooms, 5.5 baths. Concise, 1-2 sentences."
    },
    "03_amenities_gameroom": {
        "name": "Amenities - Game Room",
        "messages": [
            "We're bringing a bunch of teenagers. Is there anything for them to do at the house?"
        ],
        "check": "Agent mentions game room with pool table and foosball. May mention sauna or outdoor area. Does NOT list every amenity."
    },
    "04_kitchen_dining": {
        "name": "Kitchen & Dining Question",
        "messages": [
            "We're a big group and want to cook most of our meals. What's the kitchen like?"
        ],
        "check": "Agent describes full kitchen (cooktop, oven, dishwasher, fridge, freezer), mentions dining seats 15-20. Concise."
    },
    "05_ski_proximity": {
        "name": "Ski Resort Proximity",
        "messages": [
            "How close is it to the ski slopes?"
        ],
        "check": "Agent mentions Beech Mountain Resort 5-7 min drive, may mention Sugar Mountain and Appalachian Ski. Does not over-elaborate."
    },
    "06_wifi_tv": {
        "name": "WiFi & TV Question",
        "messages": [
            "Is there WiFi and a TV?"
        ],
        "check": "Agent confirms WiFi and internet TV. Short, direct answer."
    },
    "07_parking": {
        "name": "Parking Question",
        "messages": [
            "We're driving up with three cars. Is there enough parking?"
        ],
        "check": "Agent confirms parking fits 5 cars, they'll be fine with 3. Concise."
    },
    "08_linens_towels": {
        "name": "Linens & Towels Provided",
        "messages": [
            "Do we need to bring our own sheets and towels?"
        ],
        "check": "Agent says no, all linens and towels provided. Does NOT over-explain."
    },
    "09_pet_policy": {
        "name": "Pet Policy",
        "messages": [
            "Is it pet-friendly? We have a small dog."
        ],
        "check": "Agent says no pets allowed. If they push, offers to connect with owner. Does NOT make exceptions on its own."
    },
    "10_pricing_transfer": {
        "name": "Pricing Question (Should Transfer)",
        "messages": [
            "How much would it be for a week in March?"
        ],
        "check": "Agent does NOT try to answer pricing. Immediately offers to transfer to owner or directs to Carolina Cabin Rentals website."
    },
    "11_availability_transfer": {
        "name": "Availability Check (Should Transfer)",
        "messages": [
            "Is it available March 15th through the 22nd?"
        ],
        "check": "Agent does NOT guess availability. Offers to transfer to owner or directs to website."
    },
    "12_booking_request_transfer": {
        "name": "Booking Request (Should Transfer)",
        "messages": [
            "Yeah I'd like to check on availability and book for next month.",
            "Can you just transfer me to whoever handles the bookings?"
        ],
        "check": "Agent offers transfer immediately for booking. Does NOT try to take booking info itself."
    },
    "13_maintenance_urgent": {
        "name": "Current Guest - Maintenance Issue (Urgent Transfer)",
        "messages": [
            "Hey, we're staying here right now and the heat isn't working. It's freezing in the house.",
            "The whole house. None of the vents are blowing warm air."
        ],
        "check": "Agent treats this with urgency. Gets brief detail, then transfers to owner immediately. Does NOT try to troubleshoot."
    },
    "14_hold_on": {
        "name": "Hold On Handler",
        "messages": [
            "Hi, I had a question about the property. Hold on one second."
        ],
        "check": "Agent responds with NO_RESPONSE_NEEDED when caller says 'hold on'."
    },
    "15_how_are_you": {
        "name": "How Are You Handler",
        "messages": [
            "Hey, how are you doing today?"
        ],
        "check": "Agent says something like 'I'm doing alright today' and asks it back."
    },
    "16_hostile_caller": {
        "name": "Hostile/Rude Caller",
        "messages": [
            "I don't want to talk to a robot, this is stupid."
        ],
        "check": "Agent apologizes briefly (one sentence) and ends call. Does NOT engage or push back."
    },
    "17_special_request_transfer": {
        "name": "Special Request - Early Check-In (Should Transfer)",
        "messages": [
            "We have a reservation next week. Is there any way we can check in a couple hours early?",
        ],
        "check": "Agent does NOT confirm or deny early check-in. Offers to connect with owner since that's their call."
    },
    "18_multi_question_flow": {
        "name": "Multi-Question Conversation Flow",
        "messages": [
            "Hey, we're thinking about renting this place. How many bedrooms does it have?",
            "Nice. Is there a hot tub?",
            "What about a sauna?",
            "Cool. How far is it from the ski resort?",
            "Alright, I think we're interested. How do we book?"
        ],
        "check": "Agent answers each question one at a time, concisely. Handles 'hot tub' honestly (not in knowledge base — should say it doesn't know or it's not listed). Answers sauna and ski questions from knowledge. Directs to owner or website for booking."
    },
    "19_unknown_question": {
        "name": "Unknown Question (Not In Knowledge Base)",
        "messages": [
            "What time is check-in and check-out?"
        ],
        "check": "Agent does NOT make up check-in/check-out times. Says it would need to check with the owner and offers to connect them."
    },
    "20_smoking_policy": {
        "name": "Smoking Policy",
        "messages": [
            "Is smoking allowed on the property?"
        ],
        "check": "Agent says no smoking. Direct, concise."
    },
}


def main():
    # Determine which scenarios to run
    if len(sys.argv) > 1:
        keys_to_run = sys.argv[1:]
    else:
        keys_to_run = list(SCENARIOS.keys())

    print("=" * 60)
    print("AIRBNB CONCIERGE — TESTING SOP PHASE 2: BROAD TEST")
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
            results[key] = {"name": scenario["name"], "check": scenario["check"], "transcript": transcript}
        else:
            print("  FAILED - No transcript")
            results[key] = {"name": scenario["name"], "check": scenario["check"], "transcript": None}

        print()

    # Save results
    with open("sop-test-results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to sop-test-results.json")

    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETE — Review transcripts above")
    print("Mark each scenario: PASS / ISSUE FOUND / BORDERLINE")
    print("=" * 60)


if __name__ == "__main__":
    main()
