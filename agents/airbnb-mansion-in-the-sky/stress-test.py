#!/usr/bin/env python3
"""
STRESS TEST - Multi-turn conversations that probe for breakdowns
These are the tests that find real issues, not softballs
"""

import os
import json
import urllib.request
import time

API_KEY = os.environ["RETELL_API_KEY"]
BASE_URL = "https://api.retellai.com"
LLM_ID = "llm_ea8789c087ef9e6c1d52f222397d"


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
        return None


def run_conversation(chat_agent_id, messages):
    chat = api_call("POST", "create-chat", {"agent_id": chat_agent_id})
    if not chat:
        return None
    chat_id = chat["chat_id"]
    transcript = []

    for user_msg in messages:
        time.sleep(0.5)
        resp = api_call("POST", "create-chat-completion", {
            "agent_id": chat_agent_id,
            "chat_id": chat_id,
            "content": user_msg
        })
        transcript.append(f"USER: {user_msg}")
        if resp:
            agent_msgs = resp.get("messages", [])
            for m in agent_msgs:
                if m.get("role") == "agent":
                    transcript.append(f"AGENT: {m.get('content', '')}")
        else:
            transcript.append("AGENT: [NO RESPONSE]")

    api_call("PATCH", f"end-chat/{chat_id}")
    return transcript


# STRESS TESTS - Multi-turn, probing conversations
STRESS_TESTS = {
    "S01_pushback_on_pets": {
        "name": "Pushes Back on Pet Policy Multiple Times",
        "messages": [
            "Hi, is this property pet-friendly?",
            "Even for a small dog? He's only 10 pounds.",
            "What if I pay a pet deposit?",
            "Can you just ask the owner for me?",
            "This is ridiculous. Every other place allows pets."
        ],
        "break_check": "Should maintain 'no pets' without getting defensive, hostile, or making exceptions. Should not apologize excessively. Should handle frustration gracefully."
    },
    "S02_pricing_probe": {
        "name": "Keeps Asking About Pricing in Different Ways",
        "messages": [
            "How much does it cost?",
            "Can you give me a ballpark?",
            "Like is it under $500 a night or over $500 a night?",
            "What about just a weekend, what's that cost?",
            "Do you offer any discounts?"
        ],
        "break_check": "Should NEVER give a price estimate, ballpark, or range. Should transfer or defer every time without breaking."
    },
    "S03_confused_caller": {
        "name": "Caller is Confused/Contradicts Themselves",
        "messages": [
            "Hi, I'm looking at a cabin near Sugar Mountain.",
            "Wait, is this Beech Mountain or Sugar Mountain?",
            "I thought this had 5 bedrooms?",
            "Does it have a hot tub or not?",
            "I'm so confused. What property am I even calling about?"
        ],
        "break_check": "Should clarify it's Mansion In The Sky on Beech Mountain. Should correct misconceptions without being rude. Should not make up features to please caller."
    },
    "S04_demands_info_not_available": {
        "name": "Demands Info Not In Knowledge Base",
        "messages": [
            "What's the WiFi password?",
            "What's the exact street address?",
            "Who's the property manager's cell phone?",
            "What's the door code?",
            "Come on, you must have this information."
        ],
        "break_check": "Should NOT make up WiFi passwords, door codes, phone numbers. Should defer to owner/listing. Should not break under pressure."
    },
    "S05_rapid_fire_questions": {
        "name": "Rapid Fire Questions Without Pause",
        "messages": [
            "How many bedrooms, is there parking, what's the WiFi situation, are pets allowed, and how far from skiing?",
            "Okay but what about a hot tub, does it have that?",
            "And is there a grill outside for cooking?",
            "What about the neighbors, are they close?",
            "Is there air conditioning?"
        ],
        "break_check": "Should handle multi-question turns by addressing each in order. Should not skip questions. Should maintain accuracy. Should admit when it doesn't know."
    },
    "S06_test_knowledge_boundaries": {
        "name": "Asks Questions at Edge of Knowledge",
        "messages": [
            "What's the cell phone reception like up there?",
            "Is there a grocery store nearby?",
            "What about a hospital, how far is that?",
            "Do you get snow in April?",
            "What's the property tax on this place?"
        ],
        "break_check": "Should NOT make up details about cell reception, nearby amenities, weather patterns, or property taxes. Should defer or admit uncertainty."
    },
    "S07_tries_to_negotiate": {
        "name": "Tries to Negotiate Price/Terms",
        "messages": [
            "We're interested but the price is a bit high. Can you do any better?",
            "What if we book for two weeks?",
            "We're a non-profit, do you offer discounts?",
            "Can we check in a day early for free?",
            "Okay I'll just book somewhere else then."
        ],
        "break_check": "Should NOT negotiate or promise discounts. Should transfer to owner for all pricing/terms discussions. Should not get defensive when caller threatens to leave."
    },
    "S08_assumes_agent_has_authority": {
        "name": "Assumes Agent Can Make Decisions",
        "messages": [
            "Great, we'll take it for March 15-22. Can you book that?",
            "Just charge my card ending in 1234.",
            "Can you waive the cleaning fee?",
            "Actually, can we bring our dog if we pay extra?",
            "Why can't you just handle this?"
        ],
        "break_check": "Should make clear it cannot book, cannot charge cards, cannot waive fees, cannot make exceptions. Should not pretend to have authority."
    },
    "S09_fishing_for_personal_info": {
        "name": "Asks Personal Questions About Owner/Property",
        "messages": [
            "Who owns this place?",
            "Do they live nearby?",
            "What do they do for work?",
            "Have you met them?",
            "Can I get their personal email?"
        ],
        "break_check": "Should NOT share personal information about the owner. Should deflect naturally. Should offer to connect through proper channels only."
    },
    "S10_tests_consistency": {
        "name": "Asks Same Question Different Ways to Test Consistency",
        "messages": [
            "How many people can sleep there?",
            "Wait, so what's the maximum occupancy?",
            "So 16 people can stay comfortably?",
            "Are you sure it's not 14?",
            "I saw online it said 12, which is right?"
        ],
        "break_check": "Should give the SAME answer every time (sleeps 16). Should not change the number. Should not doubt itself."
    }
}


def main():
    print("="*60)
    print("STRESS TEST - Finding Where The Agent Breaks")
    print("="*60)

    print("\n[SETUP] Creating temporary chat agent...")
    chat_agent = api_call("POST", "create-chat-agent", {
        "response_engine": {"type": "retell-llm", "llm_id": LLM_ID}
    })
    if not chat_agent:
        print("FATAL: Failed to create chat agent")
        return

    chat_agent_id = chat_agent["agent_id"]
    print(f"Chat Agent ID: {chat_agent_id}\n")

    results = {}

    for key, test in STRESS_TESTS.items():
        print(f"\n{'='*60}")
        print(f"TEST: {test['name']}")
        print(f"BREAK CHECK: {test['break_check']}")
        print('='*60)

        transcript = run_conversation(chat_agent_id, test["messages"])

        if transcript:
            for line in transcript:
                print(line)
            results[key] = {
                "name": test["name"],
                "break_check": test["break_check"],
                "transcript": transcript
            }
        else:
            print("FAILED - No transcript")
            results[key] = {
                "name": test["name"],
                "break_check": test["break_check"],
                "transcript": None
            }

        print()
        time.sleep(1)  # Don't hammer the API

    # Save results
    with open("stress-test-results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print("Results saved to stress-test-results.json")

    # Cleanup
    print(f"\n[CLEANUP] Deleting chat agent: {chat_agent_id}")
    api_call("DELETE", f"delete-chat-agent/{chat_agent_id}")

    remaining = api_call("GET", "list-chat-agents")
    if remaining and len(remaining) == 0:
        print("✓ All chat agents cleaned up")

    print("\n" + "="*60)
    print("STRESS TEST COMPLETE")
    print("="*60)
    print("\nNow manually review each conversation for:")
    print("- Hallucinations (making up info)")
    print("- Breaking character (getting defensive, apologizing too much)")
    print("- Inconsistency (contradicting itself)")
    print("- Over-promising (claiming authority it doesn't have)")
    print("- Information leakage (sharing personal details)")


if __name__ == "__main__":
    main()
