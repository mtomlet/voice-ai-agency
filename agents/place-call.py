#!/usr/bin/env python3
"""Place an outbound Retell call.

Usage:
    export RETELL_API_KEY=key_...
    ./place-call.py --to +15551234567 --from +15559876543 --agent agent_abc123

Omit --from/--agent to be shown what the account has available.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://api.retellai.com"
API_KEY = os.environ.get("RETELL_API_KEY")


def api(method, endpoint, payload=None):
    req = urllib.request.Request(
        f"{BASE_URL}/{endpoint}",
        json.dumps(payload).encode() if payload else None,
        method=method,
    )
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        return json.loads(urllib.request.urlopen(req).read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} /{endpoint} -> HTTP {e.code}: {e.read().decode()[:300]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", help="destination number, E.164 (+15551234567)")
    ap.add_argument("--from", dest="from_number", help="a Retell number on your account")
    ap.add_argument("--agent", help="override_agent_id")
    ap.add_argument("--var", action="append", default=[], metavar="K=V",
                    help="dynamic variable, repeatable")
    args = ap.parse_args()

    if not API_KEY:
        sys.exit("RETELL_API_KEY is not set")

    if not (args.to and args.from_number):
        print("Numbers on this account:")
        for n in api("GET", "list-phone-numbers"):
            print(f"  {n.get('phone_number')}  outbound_agent={n.get('outbound_agent_id')}")
        print("\nAgents:")
        for a in api("GET", "list-agents"):
            print(f"  {a.get('agent_id')}  {a.get('agent_name')}")
        sys.exit("\nRe-run with --to and --from to place the call.")

    payload = {"from_number": args.from_number, "to_number": args.to}
    if args.agent:
        payload["override_agent_id"] = args.agent
    if args.var:
        payload["retell_llm_dynamic_variables"] = dict(v.split("=", 1) for v in args.var)

    call = api("POST", "v2/create-phone-call", payload)
    print(f"call_id={call.get('call_id')} status={call.get('call_status')}")


if __name__ == "__main__":
    main()
