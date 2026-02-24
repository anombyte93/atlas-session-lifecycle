# Test Specification Generator Skill

## Overview

The `/test-spec-gen` skill generates comprehensive test specifications for any application through multi-agent orchestration.

## Features

- **Universal**: Works with web, desktop, mobile applications
- **Multi-Agent**: 5 explore agents + research + 5 specialist agents
- **Hierarchical Verification**: Doubt agent + Finality agent review
- **Hermes-Style Output**: TC-XXX formatted test cases
- **Traceability**: Built-in requirement-to-test mapping
- **Trello Integration**: Optional card creation

## Usage

```bash
/test-spec-gen
```

## Workflow

```
Plan Mode -> Discovery (5 agents) -> Research -> Generation (5 agents) -> Verification -> Quick-Clarify -> Trello (optional)
```

## Output

Test specification document saved to:
```
docs/test-specifications/{PROJECT_NAME}-test-spec.md
```

## Requirements

- MCP servers configured
- Test framework detected
- Runnable application
