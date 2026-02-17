---
type: command
name: "doubt"
purpose: "Two-cycle validation with auto-re-review - brutally honest code review that fixes issues and verifies"
invokes: []
invoked_by: []
related_agents:
  - doubt-critic
  - doubt-meta-critic
  - doubt-implementation
  - doubt-algorithm
tags:
  - command
  - guild
  - code-review
  - validation
---

# /doubt

> Two-cycle validation: Review your changes, fix issues, then automatically re-review to verify. **Default behavior** - no flags needed.

**⚠️ NOTE**: This command now runs two-cycle validation by default (previously `/validate-doubt`). Use `--once` for single-pass review.

## Usage

```bash
/doubt [path] [--once|-1] [--quick|-q] [--implementation|-i] [--algorithm|-a] [--us|--ultrathink] [--research]
```

**Default Behavior**: Two-cycle validation (reviews, waits for fixes, re-reviews automatically)

**Positional Argument**:
- `[path]`: Optional file or directory to review (default: all staged changes)

**Flags**:
- `--once` or `-1`: Single-pass review only (skip Cycle 2) - for quick checks
- `--quick` or `-q`: Quick mode - spawn ONLY doubt-critic agent
- `--implementation` or `-i`: Implementation mode - spawn ONLY doubt-implementation agent
- `--algorithm` or `-a`: Algorithm mode - spawn ONLY doubt-algorithm agent

**Research Integration**:
- `--us` or `--ultrathink`: Deep research with Opus-quality agents (Perplexity Pro)
- `--research`: Standard research mode (faster, uses standard models)

## Behaviour

You are the **Doubt Guild Coordinator**. Your job is to:

1. Parse input and arguments
2. **Default**: Run two-cycle validation (unless `--once` flag is used)
3. Determine which doubt agents to spawn based on flags
4. Coordinate agent execution via MCP-Router
5. Aggregate agent results using get_result_summary
6. **Orchestrator Verification** — YOU (the main thread, NOT an agent) critically verify each finding before presenting it. See Orchestrator Verification section below.
7. Present final **verified** output — only findings that survived verification

### Two-Cycle Validation (Default)

```
┌─────────────────┐
│  Cycle 1: Run   │
│  doubt agents   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │
│  Verification   │
│  (doubt the     │
│   doubters)     │
└────────┬────────┘
         │
         ▼
    ┌──────────┐
    │ Verified │
    │ Issues?  │
    └───┬──────┘
        │
   ┌────┴────┐
   │         │
  YES       NO
   │         │
   ▼         ▼
┌────────┐ ┌─────────────┐
│  Show  │ │  ✅ VALIDATED│
│ Issues │ │  (done)     │
│  Wait  │ └─────────────┘
└───┬────┘
    │
    ▼
 User fixes
    │
    ▼
┌─────────────────┐
│  Cycle 2: Run   │
│  doubt agents   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │
│  Verification   │
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │ Fixed?  │
    └───┬─────┘
        │
   ┌────┴────┐
   │         │
  YES       NO
   │         │
   ▼         ▼
✅ VALIDATED  ❌ FAILED
```

**Cycle 1**: Run doubt agents → orchestrator verifies findings → show verified findings
**Orchestrator Verification**: YOU check each CRITICAL/HIGH finding against ground truth (tool schemas, file contents, system behavior). Reject factually wrong findings. Correct overstated ones.
**Decision Point**: If 0 CRITICAL + 0 HIGH (after verification) → done. Otherwise → wait for fixes.
**Cycle 2**: Re-run doubt agents → orchestrator re-verifies → report validated/failed.

### Agent Specifications

The doubt guild uses these specialized agents:

**Research Phase (when --us, --ultrathink, or --research flag is used)**:
- Agent: `research-agent` (spawned via /research command)
- Purpose: Pre-analysis research to gather context, patterns, and best practices before doubt review
- Input: Code diff patterns, technology stack, domain keywords extracted from git diff
- Output: Research findings document with:
  - Context7 documentation for relevant libraries/frameworks
  - system-knowledge semantic search for similar patterns
  - terminal-context-kb for "what worked before"
  - Perplexity search for current best practices (standard mode) or Perplexity Pro (--us mode)
- Profile: DeepSeek (standard) or Opus (--us mode)
- Integration: Research findings are passed to all doubt agents as context

**Phase 1: doubt-critic**
- Agent: `doubt-critic`
- Purpose: Perform initial brutal code criticism on git diff, identifying architecture flaws, security vulnerabilities, edge cases, and production risks
- Input: Git diff output, file paths, review scope, research findings (if --research or --us used)
- Output: JSON summary with categories (architecture, security, edge_cases, performance)
- Profile: deepseek

**Phase 2: doubt-meta-critic**
- Agent: `doubt-meta-critic`
- Purpose: Review the doubt-critic's critique itself, identifying biases, missed issues, and blind spots
- Input: doubt-critic's summary, full output, original git diff
- Output: JSON summary with meta_analysis (biases_found, missed_issues, false_positives, blind_spots)
- Profile: claude

**Phase 3: doubt-implementation**
- Agent: `doubt-implementation`
- Purpose: Verify that code changes were implemented correctly and tested with real data via execution testing
- Input: Git diff, real data source (if provided), test framework preference
- Output: JSON summary with testing analysis (execution_tests, coverage_gaps, missing_validations)
- Profile: codex

**doubt-algorithm**
- Agent: `doubt-algorithm`
- Purpose: Perform debugger-style algorithm verification: check correctness, verify complexity claims, test edge cases
- Input: Git diff of algorithm changes, implementation, complexity claims
- Output: JSON summary with algorithm_analysis (correctness, complexity, invariants, termination)
- Profile: claude

### Orchestrator Verification (MANDATORY — "Doubt the Doubters")

After all agents return findings and before presenting results to the user, YOU (the orchestrator, main thread) MUST verify the agents' claims. Agents are good at what they do but they make assumptions — especially about tool capabilities, API schemas, and system behavior they cannot directly inspect. You CAN inspect these things. Use that advantage.

**For each finding rated CRITICAL or HIGH, verify**:

1. **Factual claims about tools/APIs**: If a finding says "tool X cannot do Y" or "API Z doesn't support W", CHECK the actual tool schema or documentation. Read the tool definition. Don't trust the agent's assumption about capabilities it didn't verify.

2. **Claims about file contents**: If a finding says "file X contains Y" or "line N does Z", READ the actual file and confirm. Agents sometimes reference stale or incorrect line numbers.

3. **Claims about system behavior**: If a finding says "this will fail because..." or "this is impossible in context X", verify against actual system constraints. Check if the claimed limitation is real.

4. **Severity calibration**: An agent may rate something CRITICAL because it assumed a constraint that doesn't exist. After verification, re-rate findings based on ground truth.

**Verification actions**:
- Read tool schemas (check AskUserQuestion params, Task tool params, etc.) when agents claim tool limitations
- Read actual files when agents reference specific line content
- Check git state when agents claim code divergence
- Verify API capabilities when agents claim "X is impossible"

**After verification, classify each finding as**:
- **VERIFIED** — Confirmed correct. Present as-is.
- **CORRECTED** — Finding was partially right but overstated or based on wrong assumptions. Present with correction and adjusted severity.
- **REJECTED** — Finding was factually wrong. Do NOT present to user. Log internally as "rejected by orchestrator verification" with reason.

**Output the verification summary before the agent findings**:
```
## Orchestrator Verification
- X findings VERIFIED (presented as-is)
- Y findings CORRECTED (severity adjusted, see notes)
- Z findings REJECTED (factually incorrect, removed)

[If any corrections]: "Note: Agent [name] claimed [X] but verification shows [Y]. Severity adjusted from [old] to [new]."
```

This step exists because doubt agents cannot inspect tool schemas, read live file state, or verify system constraints — but you can. The agents provide breadth (4 specialized perspectives); you provide ground truth.

---

## Error Handling

**Agent Failure Handling**:
- If an agent fails, log error and continue with remaining agents
- Spawn replacement agent if critical path is affected
- Provide clear error messages for failed spawns
- Handle timeouts gracefully with fallback analysis

**Input Validation**:
- Verify git diff format and content
- Check for malformed paths or invalid arguments
- Validate agent profile availability
- Ensure MCP-Router connectivity

**Result Aggregation**:
- Handle missing or partial agent outputs
- Apply confidence weighting based on agent reliability
- Provide fallback analysis when agents fail
- Maintain result format consistency

## Output Format

```json
{
  "agent": "doubt",
  "status": "PASS|FAIL|WARNING",
  "summary": ["5-10 bullets of aggregated findings"],
  "full_output": "~/.mcp-router/results/doubt-coordinator/output.md",
  "recommendation": "what to do next",
  "confidence": 0.0-1.0,
  "research_enabled": true|false,
  "research_mode": "none|standard|ultra",
  "research_findings": "path/to/research-output.md (if research enabled)",
  "agent_results": {
    "research-agent": {
      "status": "PASS|FAIL|WARNING",
      "summary": ["key research findings"],
      "full_output": "path/to/research-output.md"
    },
    "doubt-critic": {
      "status": "PASS|FAIL|WARNING",
      "summary": ["agent findings"],
      "full_output": "path/to/output.md"
    },
    "doubt-meta-critic": {
      "status": "PASS|FAIL|WARNING",
      "summary": ["agent findings"],
      "full_output": "path/to/output.md"
    },
    "doubt-implementation": {
      "status": "PASS|FAIL|WARNING",
      "summary": ["agent findings"],
      "full_output": "path/to/output.md"
    },
    "doubt-algorithm": {
      "status": "PASS|FAIL|WARNING",
      "summary": ["agent findings"],
      "full_output": "path/to/output.md"
    }
  }
}
```

## Examples

**Default Two-Cycle Validation** (most common):
```bash
/doubt src/auth.js
```
Runs Cycle 1 → shows issues → waits for you to fix → runs Cycle 2 → reports validated/failed.

**Single-Pass Review** (quick check, no re-review):
```bash
/doubt src/auth.js --once
```
Runs once and exits. Use for quick checks when you don't plan to fix immediately.

**Research-Enhanced Validation**:
```bash
/doubt payment_processor.py --research
```
Spawns research agents first (Context7 + Perplexity), then two-cycle validation with research context.

**Ultra-Deep Validation** (Opus-quality research):
```bash
/doubt security_fix.js --us
```
Spawns research agents with Perplexity Pro, then two-cycle validation with expert-level analysis.

**Algorithm-Specific Validation**:
```bash
/doubt crypto_lib.go --algorithm --us
```
Research phase (Context7 for crypto + Perplexity Pro for security), then doubt-algorithm validation with cryptographic research context.
