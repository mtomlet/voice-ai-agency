# PI Intake Agent — Issue Log

## Testing Session: Feb 11, 2026

### ISSUE #1: Email dash-spelling never fired
- **Scenario**: All email collection scenarios (1, 2, 3, 5, 6)
- **Failure**: Agent skipped spelling step entirely, just said "Thank you" and moved on
- **Frequency**: 5/5 scenarios failed (systemic)
- **Root cause**: Instructions in Step 4 ignored by GPT-4.1; also discovered Retell LLM caching issue — updating existing LLM via API doesn't propagate to new chat agents
- **Fix applied**: Added CRITICAL OVERRIDE section at top of prompt, created Step 4.5 with explicit stop-and-spell pattern, created new LLM (cache bust)
- **Fix version**: "Override Primacy" → "Fresh LLM"
- **Verified**: PASS — all 5 email scenarios now spell with dashes

### ISSUE #2: "Hold on" handler broken
- **Scenario**: Caller says "hold on" mid-conversation
- **Failure**: Agent said "Of course, take your time" instead of NO_RESPONSE_NEEDED
- **Frequency**: 2/2 (confirmed)
- **Root cause**: GPT-4.1 helpfulness bias overrode instruction; also LLM caching
- **Fix applied**: OVERRIDE 3 at top of prompt + Example Call 7 + new LLM
- **Fix version**: "Fresh LLM"
- **Verified**: PASS — empty response (silent)

### ISSUE #3: "How are you" handler broken
- **Scenario**: Caller asks "how are you" as first message
- **Failure**: Agent reintroduced itself instead of asking back
- **Frequency**: 2/2 (confirmed)
- **Root cause**: Chat API doesn't send begin_message, so model defaulted to introduction; also LLM caching
- **Fix applied**: OVERRIDE 4 at top + Step 1 branching + Example Call 7 + new LLM
- **Fix version**: "Fresh LLM"
- **Verified**: PASS — "I'm doing alright today. Uh, how are you?"

### ISSUE #4: Prompt instruction leakage in urgent transfer
- **Scenario**: Urgent caller, agent attempts transfer
- **Failure**: Agent output "[If transfer fails: ...]" as literal dialogue
- **Frequency**: 2/2 (confirmed)
- **Root cause**: Bracketed text in Urgency section looked like output to the model
- **Fix applied**: Removed all brackets, restructured as natural IF/THEN steps, added OVERRIDE 5 + new LLM
- **Fix version**: "Fresh LLM"
- **Verified**: PASS — natural flow, no leakage

### ISSUE #5: Hostile caller didn't follow script
- **Scenario**: Hostile/rude caller
- **Failure**: Agent gave office hours instead of "I'm sorry for the trouble. Have a good night." → end_call
- **Frequency**: 2/2 (confirmed)
- **Root cause**: GPT-4.1 helpfulness bias; also LLM caching
- **Fix applied**: OVERRIDE 2 at top + explicit "DO NOT offer office hours" + Example Call 8 + new LLM
- **Fix version**: "Fresh LLM"
- **Verified**: PASS — exact script + end_call triggered

---

## Key Discovery: Retell LLM Caching

**Updating an existing LLM via `PATCH update-retell-llm` does NOT propagate changes to new chat agents.** The prompt changes are stored but the runtime uses a cached version. Creating a brand new LLM with the same prompt works immediately.

**Workaround**: When making significant prompt changes, create a new LLM rather than updating the existing one. Then update the agent's response engine (note: can only do this before first publish; after publish, must create new agent).

---

## Regression Result
- **Date**: Feb 11, 2026
- **LLM**: llm_e84132673b1e896388a5bd467d62
- **Agent**: agent_a3a30a67fcc03e1be7bfe2e362
- **Result**: 11/11 scenarios PASS
- **Status**: All issues resolved, regression clean
