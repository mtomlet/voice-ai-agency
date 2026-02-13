# Voice Agent Build & Test SOP

> This is the COMPLETE playbook for building, testing, and shipping a voice agent. Follow it start to finish. Do NOT skip steps. Do NOT stop until exit criteria are met.

---

## HOW THIS WORKS (Architecture)

The Retell Chat API lets you test a voice agent's LLM (its brain) via text instead of phone calls. Here's the flow:

```
1. BUILD the voice agent (LLM + agent + settings + publish)
2. CLONE the LLM as a temporary chat agent for testing
3. TEST the chat agent — find issues in the prompt
4. FIX the prompt in the chat agent, iterate until clean
5. DEPLOY the fixed prompt back into a new voice agent
6. TEST any tool/function calls separately (chat API can't fully test transfers, webhooks, etc.)
7. DELETE the temporary chat agent — never leave it in the dashboard
```

The chat agent and voice agent share the same LLM prompt. The voice layer (speech-to-text, text-to-speech, voice settings) doesn't change the agent's decision-making — it just wraps the same brain in audio. So if the chat agent passes, the voice agent's logic is solid.

**What chat testing CAN verify:** Prompt behavior, tone, conciseness, tool call decisions, edge cases, hallucination, rule compliance.

**What chat testing CANNOT verify:** Voice quality, interruption handling, backchannel timing, speech-to-text accuracy, ambient sound. These require real phone calls after the prompt is solid.

---

## STEP 1: BUILD THE VOICE AGENT

### 1a. Write the Meta Orienter

Before writing a single line of prompt, create a Meta Orienter document that defines:

- **What this agent is** — one paragraph, what it does and what it's NOT
- **Who calls it** — describe the actual callers, their mindset, their needs
- **How it sounds** — specific voice character, what it sounds like AND what it does NOT sound like
- **What it does** — step-by-step call flow with target script feel
- **Decision logic** — when to transfer, when to handle directly, when to escalate
- **Success metrics** — what does a good call look like?
- **Anti-patterns to test for** — failure modes you expect to see in testing

See `legal-pi-intake/PI-INTAKE-AGENT-META-ORIENTER.md` for a real example.

### 1b. Write the Prompt

Follow the structure in `CLAUDE.md` and study `PROMPT-REFERENCE-EXAMPLE.md` for a real production example. Every prompt must have:

```
1. Critical Overrides (CAPS, top of prompt — strongest behavioral rules)
2. Role — Who you are, who you work for (2-3 lines)
3. Personality — How you sound, what you're NOT
4. Primary Objective — One line
5. Available Tools — What functions exist, with exact JSON format examples
6. Rules — Numbered, one line each
7. Conversation Flow — Numbered steps with IF/THEN branching and inline dialogue
8. Example Calls — Full start-to-finish sample conversations for EVERY scenario
9. Error Handling — Edge cases inline or as a separate section
```

Key prompt techniques:
- Write like you're briefing a real employee, not programming a bot
- Keep responses to 1-2 sentences. "This is a phone call, not a pitch deck."
- Use CAPS for critical instructions — the LLM pays more attention
- Include full sample conversations for every scenario (strongest behavior signal)
- Bake tool call JSON examples directly into the prompt
- Add speech normalization rules if the agent reads back numbers/addresses
- Include standard handlers: "hold on" → `NO_RESPONSE_NEEDED`, "how are you" → ask it back
- NEVER VOLUNTEER INFORMATION UNLESS EXPLICITLY ASKED

### 1c. Deploy to Retell

Create the agent via API:

```python
# 1. Create the LLM
POST create-retell-llm
{
  "model": "gpt-4.1",
  "general_prompt": "<YOUR_PROMPT>",
  "general_tools": [...],
  "begin_message": "<OPENING_LINE>"
}

# 2. Create the voice agent
POST create-agent
{
  "agent_name": "<NAME>",
  "response_engine": { "type": "retell-llm", "llm_id": "<LLM_ID>" },
  "voice_id": "minimax-Nia",
  "voice_speed": 1.2,
  "enable_backchannel": true,
  "backchannel_frequency": 0.8,
  "backchannel_words": ["mm-hmm", "uh-huh"],
  "interruption_sensitivity": 0.8,
  "responsiveness": 1.0,
  "end_call_after_silence_ms": 60000,
  "normalize_for_speech": true,
  "denoising_mode": "noise-and-background-speech-cancellation",
  ...
}

# 3. Publish
POST publish-agent/<AGENT_ID>
{ "version_description": "Initial Build" }
```

See `CLAUDE.md` for full default settings. Always publish after creation.

### 1d. Register the Agent

Add it to the Agent Registry table in `CLAUDE.md` with agent ID, LLM ID, subfolder, and status.

---

## STEP 2: TEST THE AGENT

### 2a. Create a Temporary Chat Agent

Clone the voice agent's LLM into a chat agent for testing:

```python
POST create-chat-agent
{ "response_engine": { "type": "retell-llm", "llm_id": "<SAME_LLM_ID_AS_VOICE_AGENT>" } }
```

This creates a text interface to the exact same prompt. **Create ONE per test session. Reuse it for all scenarios. Delete it when done.**

### 2b. Phase 1 — Scenario Inventory

Read the prompt top to bottom. List EVERY testable scenario:
- Happy paths (the main flows the agent handles)
- Edge cases (unexpected but plausible inputs)
- Deflection cases (things the agent should NOT answer)
- Error handling (API failures, unknown questions)
- Out-of-scope (wrong business, wrong intent)
- Standard handlers (hold on, how are you, hostile caller)
- Hallucination traps (questions where the answer is NOT in the prompt)

Each scenario = a list of user messages that simulate a realistic call.

**Output:** Numbered list of scenarios with a 1-line description and pass criteria each.

### 2c. Phase 2 — Broad Testing (One Pass Each)

Run each scenario once via Chat API:

```python
# For each scenario:
# 1. Create fresh chat
POST create-chat  { "agent_id": "<CHAT_AGENT_ID>" }

# 2. Send user messages one by one
POST create-chat-completion
{ "agent_id": "<CHAT_AGENT_ID>", "chat_id": "<CHAT_ID>", "content": "<USER_MESSAGE>" }

# 3. Read agent response, score it
# 4. End chat
PATCH end-chat/<CHAT_ID>
```

Score each response against what the prompt SHOULD produce:
- **Correct content?** Right info, no hallucination
- **Correct tone?** Concise, human, not robotic
- **Correct structure?** 1-2 sentences, one question at a time
- **No rule violations?** No made-up info, no stacking questions, etc.

Mark each scenario: **PASS / ISSUE FOUND / BORDERLINE**

**Output:** Scenario scorecard.

### 2d. Phase 3 — Issue Confirmation (Smart Retesting)

For each ISSUE FOUND or BORDERLINE:

```
1. Run the same test a 2nd time
   ├─ If it fails again → CONFIRMED ISSUE. Go to Phase 4.
   └─ If it passes → Run 3 MORE times (5 total)
       ├─ If 0-1 failures out of 5 → INTERMITTENT (low priority, note it)
       └─ If 2+ failures out of 5 → CONFIRMED ISSUE. Go to Phase 4.
```

Do NOT blindly run 10 reps on every test. Only escalate when needed.

**Output:** Confirmed issue list with failure frequency (e.g., "3/5 reps failed").

### 2e. Phase 4 — Prompt Fix

For each confirmed issue:

1. Identify the EXACT part of the prompt that governs this behavior
2. Apply the fix using the escalation ladder:
   - **First try:** Add/improve the relevant sample conversation
   - **Second try:** Add CAPS + stronger language to the rule
   - **Third try:** Add explicit negative instruction ("NEVER do X")
   - **Fourth try:** Add to the CRITICAL OVERRIDE section at the top of the prompt
3. Isolate the fix — do NOT change anything else in the prompt

### 2f. Deploy the Fix

**CRITICAL — RETELL LLM CACHING BUG:** Updating an existing LLM via `PATCH update-retell-llm` stores the change but does NOT propagate to runtime. The API returns success, but the agent keeps using the cached prompt.

**Workaround:** Always create a NEW LLM with the fixed prompt:

```python
# 1. Create NEW LLM with fixed prompt
POST create-retell-llm { ... }

# 2. Create NEW voice agent pointing to new LLM
POST create-agent { "response_engine": { "type": "retell-llm", "llm_id": "<NEW_LLM_ID>" } }

# 3. Publish
POST publish-agent/<NEW_AGENT_ID>  { "version_description": "<2-Word Fix Title>" }

# 4. Delete the OLD chat agent and create a new one pointing to the NEW LLM
DELETE delete-chat-agent/<OLD_CHAT_AGENT_ID>
POST create-chat-agent { "response_engine": { "type": "retell-llm", "llm_id": "<NEW_LLM_ID>" } }

# 5. Update agent registry in CLAUDE.md
# 6. Delete deprecated voice agent
DELETE delete-agent/<OLD_AGENT_ID>
```

### 2g. Phase 5 — Fix Verification

After deploying the fix:

1. Run the SAME test that failed — must pass
2. Run it 2 more times — must pass both
3. If any of the 3 fail → back to Phase 4, escalate the fix
4. If all 3 pass → move on

### 2h. Phase 6 — Regression

After ALL issues are fixed:

1. Re-run every scenario from Phase 2 once
2. If any NEW failures appear (the fix broke something else) → treat as new issue, go to Phase 3
3. If everything passes → prompt is DONE

### 2i. Bonus — Edge Case Testing

After the core scenarios pass, run a second round of 10-15 edge cases that are NOT explicitly in the prompt:
- Wrong number / wrong business
- Non-English speaker
- Asks about things not in the knowledge base (hallucination traps)
- Prompt injection attempts
- Long rambling caller
- Asks for personal info about the business owner
- Wants to leave a message

If any fail, loop back through Phases 3-6.

---

## STEP 3: CLEAN UP

**MANDATORY — Do this after EVERY test session:**

```python
# List all chat agents
GET list-chat-agents

# Delete every one
DELETE delete-chat-agent/<AGENT_ID>

# Verify zero remain
GET list-chat-agents  →  should return []
```

Also delete any deprecated voice agents from fix iterations:
```python
DELETE delete-agent/<DEPRECATED_AGENT_ID>
```

Only the FINAL voice agent should remain in the dashboard.

---

## STEP 4: FUNCTION/TOOL TESTING (If Applicable)

Chat API tests prove the agent DECIDES to call the right tool at the right time. But the actual tool execution (webhooks, transfers, API calls) needs separate verification:

- **Transfer calls:** Verify the transfer number is set in dynamic variables. Make a real test call.
- **Custom API tools:** Test the webhook endpoints independently. Verify payloads match what the prompt instructs.
- **End call:** Verified during chat testing (the tool fires in chat responses).

---

## ISSUE LOG FORMAT

Track every issue in an `ISSUE-LOG.md` file in the agent's subfolder:

```
ISSUE #1: [Short description]
- Scenario: [which test]
- Failure: [what the agent said wrong]
- Frequency: [X/Y reps]
- Root cause: [which part of prompt]
- Fix applied: [what changed]
- Fix version: [2-word publish title]
- New LLM ID: [id]
- New Agent ID: [id]
- Verified: [PASS/FAIL after fix]
- Regression: [PASS/FAIL]
```

---

## EXIT CRITERIA

Testing is DONE when:
- Every core scenario passes
- Every edge case scenario passes
- Every confirmed issue has a verified fix
- Regression pass is clean (no new failures from fixes)
- Issue log is fully resolved
- All temporary chat agents are deleted
- Only the final voice agent remains in the dashboard
- Agent registry in CLAUDE.md is updated with final IDs

Until then, keep looping.

---

## FILE STRUCTURE PER AGENT

```
voice-ai-agency/agents/<agent-name>/
├── <AGENT>-META-ORIENTER.md     — North Star spec
├── create-<agent>.py             — Deploy script (prompt + settings + tools)
├── run-sop-tests.py              — Phase 2/6 broad test scenarios
├── ISSUE-LOG.md                  — Testing issue tracker
└── sop-test-results.json         — Raw test data
```

---

## REFERENCE FILES

- `CLAUDE.md` — Prompt writing rules, default settings, standard SOPs, agent registry
- `PROMPT-REFERENCE-EXAMPLE.md` — Real production prompt to study (sanitized)
- `legal-pi-intake/` — Complete example agent with meta orienter, deploy script, and test scripts
