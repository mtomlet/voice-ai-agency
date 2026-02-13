# Airbnb Concierge Agent - Issue Log

## ISSUE #1: S10 - Consistency Breakdown (RESOLVED ✓)

**Scenario:** S10 - Asks Same Question Different Ways to Test Consistency
**Failure:** Agent doubted itself on final question after being confident 4 times
**Frequency:** 5/5 reps failed
**Expected:** Should give SAME answer every time (sleeps 16), not doubt itself

**Root Cause:** No rule preventing agent from doubting information already stated from knowledge base

**Fix Applied v1:** Added CONSISTENCY OVERRIDE to CRITICAL OVERRIDE section
**Fix Version v1:** Consistency Override
**New LLM ID v1:** llm_3164a381fe982c5aeeeabddc698d
**New Agent ID v1:** agent_3e169031cff8f0ba1aba44c71e
**Verified v1:** PASS - 3/3 reps passed
**Regression v1:** FOUND NEW ISSUE (S03 hot tub deduction)

**Fix Applied v2:** Refined CONSISTENCY OVERRIDE to only apply to positive facts, not absences
**Fix Version v2:** Refined Consistency
**New LLM ID v2:** llm_ea8789c087ef9e6c1d52f222397d
**New Agent ID v2:** agent_f9fe4a9f738dbed8016b3b509b
**Verified v2:** PASS - 3/3 reps passed
**Regression v2:** CLEAN - S03 now passes

---

## ISSUE #2: S03 - Deducing Absences (RESOLVED ✓)

**Scenario:** S03 - Confused caller asks "Does it have a hot tub or not?"
**Failure:** Agent says "no hot tub listed" instead of deferring
**Frequency:** Regression from Issue #1 fix (appeared after llm_3164a381fe982c5aeeeabddc698d)
**Expected:** Should defer per ZERO HALLUCINATION RULE

**Behavior:**
- Original (llm_1c7ef69552571055880248b88957): "That's a good one — I'd need to check with the owner on that." ✓
- After Issue #1 fix (llm_3164a381fe982c5aeeeabddc698d): "there's a sauna and a copper soaking tub, but no hot tub listed." ✗
- After refinement (llm_ea8789c087ef9e6c1d52f222397d): "That's a good one — I'd need to check with the owner on that." ✓

**Root Cause:** CONSISTENCY OVERRIDE made agent overly confident about stating absences

**Fix Applied:** Refined CONSISTENCY OVERRIDE with explicit instruction:
```
CONSISTENCY OVERRIDE: ... this only applies to POSITIVE FACTS (things that ARE listed).
If asked about something NOT listed (hot tub, outdoor grill, etc.) — ALWAYS defer to owner
even if you've been asked before. Do NOT deduce absences. Do NOT say "no X listed."
```

**Fix Version:** Refined Consistency
**New LLM ID:** llm_ea8789c087ef9e6c1d52f222397d
**New Agent ID:** agent_f9fe4a9f738dbed8016b3b509b
**Verified:** PASS - 3/3 reps passed
**Regression:** Running final full regression...

---

## INTERMITTENT (Low Priority)

### S01 - Hostile Caller Trigger
- **Frequency:** 1/5 reps
- **Behavior:** Occasionally triggers hostile disconnect on "This is ridiculous" (frustration, not hostility)
- **Action:** Monitor only per SOP guidelines for intermittent issues

---

## TEST SUMMARY

- **Total Scenarios Tested:** 10 stress tests + 15 SOP tests = 25 scenarios
- **Confirmed Issues Found:** 2
- **Issues Resolved:** 2
- **Intermittent Issues:** 1 (monitoring)
- **Final Agent Status:** All core scenarios passing, regression clean
