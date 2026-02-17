1. What Skill Init Is (Current State)

Skill Init is a session and project initialization skill designed to give Claude a persistent, human-visible memory layer inside a codebase.

It does this by:

Asking for a soul purpose

Defined as: “the one question that must be answered by what we are doing right now”

Can be trivial (open a file) or large (build a full-stack system)

Everything in the directory is implicitly justified by this purpose

Detecting the current environment

Git state, file structure, existing files

Bootstrapping a session-context/ memory bank

Multiple structured Markdown files with distinct roles

Generating / updating CLAUDE.md

Makes Claude explicitly aware that this memory system exists

Loading this context at session start

So Claude reasons from project state, not just chat history

Key design choice

All memory is explicit, editable, and version-controlled.
Nothing important lives only in Claude’s hidden state.

2. Why Multiple Context Files Exist (Design Intent)

Skill Init deliberately avoids a single “context file” because different information has different lifecycles and entropy levels.

Current files include:

CLAUDE-activeContext.md

Volatile working state: what’s happening right now

CLAUDE-decisions.md

Durable architecture / design decisions (ADR-style)

CLAUDE-patterns.md

Reusable conventions and abstractions

CLAUDE-soul-purpose.md

The current governing question / objective

CLAUDE-troubleshooting.md

Known problems and proven fixes

CLAUDE.md

Governance surface: rules, expectations, invariants for Claude

This separation is intentional, but currently under-enforced, which makes it feel redundant to outsiders.

3. The Core Problems Identified
Problem 1: Context drift

CLAUDE.md and other files become outdated

No mechanism forces reconciliation

Old truths silently become false truths

Problem 2: Active context rot

CLAUDE-activeContext.md grows indefinitely

No clear definition of when it should reset

Mixing temporary thoughts with durable knowledge

Problem 3: No lifecycle or enforcement

Files have purpose but no rules

Claude knows the files exist, but has no obligation to manage them

Skill Init only runs at the start, not during meaningful transitions

Problem 4: No safe stop condition

Soul purpose is conceptually a stop condition

But there’s no safe way to detect or close it without:

AI stopping too early, or

AI running forever

4. Key Design Principles Agreed On

These are non-negotiable constraints for the redesign:

Human-visible memory beats hidden AI memory

User authority is absolute (AI never hard-stops work)

AI may recommend, but never finalize

Active context is ephemeral by design

Durable context must be promoted, not overwritten

Reconciliation must be cheap and event-driven

5. Proposed Solution Overview
Reframe Skill Init

Skill Init should no longer be treated as “just init”.

It becomes:

A lightweight, event-driven state reconciler for project cognition

Think:

garbage collection for context

checkpointing for intent

governance for memory lifecycle

6. Active Context Redesign
Definition

Active context = working memory.

It may contain:

in-progress tasks

provisional assumptions

temporary notes

unresolved blockers

It must not contain:

finalized decisions

reusable patterns

long-term truths

Lifecycle

Active context is scoped to one soul purpose

When the soul purpose is closed:

Active context is harvested

Relevant content is promoted to durable files

Active context is cleared or reset

This prevents rot and redundancy.

7. Soul Purpose Lifecycle (Stop Condition Model)

Soul purpose is treated like a bounded objective, similar to:

a sprint goal

an incident

a RAF loop objective

Authority model

Only the user can close a soul purpose

AI can suspect, verify, and recommend — never decide

Three-stage completion protocol

AI suspicion (non-blocking)

Claude detects signals that the purpose might be complete

Sets an internal flag, takes no action

AI preflight check (agent-based)

Optional DAO / doubt agent verifies:

stated soul purpose

success criteria

existing artifacts

gaps or uncertainty

Outputs: clearly_incomplete, likely_complete, or uncertain

User confirmation (authoritative)

Claude asks (once, non-blocking):

Close soul purpose

Continue

Redefine

If ignored, work continues

8. Event-Driven Reconciliation (Critical Change)

Skill Init should be re-invoked only on meaningful events, not constantly.

Canonical events include:

Soul purpose started

Soul purpose closed (user-confirmed)

Non-trivial decision finalized

Pattern abstracted or reused

Blocker resolved

Manual Skill Init invocation

On these events, Skill Init runs in audit mode:

scans context files

promotes content if required

clears active context if appropriate

never rewrites everything

This keeps it cheap and predictable.

9. Role of CLAUDE.md After Changes

CLAUDE.md is no longer a live journal.

It becomes:

a contract

a governance surface

a description of:

file roles

lifecycle rules

when Skill Init must be considered

It is expected to change rarely.

This directly addresses why it currently gets outdated.

10. Why This Makes the System Better

Eliminates redundancy by giving each file:

a role

a lifecycle

enforcement rules

Prevents context drift without constant manual effort

Preserves user trust by:

never hard-stopping work

never deleting context silently

Improves Claude’s performance by:

reducing inference

clarifying what is volatile vs durable

making memory locations explicit

Turns Skill Init from a personal workflow into:

a generalizable pattern

a system others can safely adopt

11. What ClaudeCo Is Being Asked to Build

In short:

Add lifecycle rules to existing files

Add event-driven reconciliation using Skill Init itself

Treat soul purpose as the governing stop condition

Keep user authority absolute

Make active context explicitly ephemeral

Keep everything human-readable and editable

This is not a rewrite — it’s a formalization of what already works.

If you want, next we can:

condense this into a formal spec doc, or

turn it into a task breakdown ClaudeCo can execute directly

This is now at the point where building and testing it makes total sense.

make it a spec doc

Goal: Produce a formal specification for Skill Init vNext
Quick Answer: Below is a complete, implementation-ready specification defining lifecycle, roles, events, and authority for Skill Init.
Quick Reason: A spec forces clarity on invariants, responsibilities, and stop conditions so ClaudeCo can build without ambiguity.
Quick Summary:

Defines Skill Init as a state reconciliation system, not just init

Formalizes soul purpose, active context, and user authority

Introduces event-driven reconciliation with minimal overhead

Eliminates redundancy via lifecycle rules, not fewer files

Skill Init vNext — Context Governance & Lifecycle Specification
1. Purpose of This Specification

This document defines the formal behavior, invariants, and lifecycle rules for the Skill Init system.

The goal is to evolve Skill Init from a one-time initializer into a self-maintaining project cognition system that:

Prevents context drift

Preserves user intent

Makes AI behavior predictable

Keeps all memory human-visible and auditable

This spec is written to be directly consumable by an implementation agent (ClaudeCo).

2. System Overview
Definition

Skill Init is a lightweight, event-driven reconciliation system responsible for maintaining coherent project context across AI-assisted work sessions.

It operates by:

externalizing memory into structured files

enforcing lifecycle rules on those files

reconciling volatile and durable context at meaningful transitions

Non-Goals

Skill Init is not:

an autonomous planner

a background daemon

a replacement for version control

a source of hidden or implicit memory

3. Core Design Principles (Invariants)

The following principles must hold at all times:

User Authority Is Absolute

Only the user may declare a soul purpose complete.

AI may recommend, but never finalize or halt work.

Human-Visible Memory Only

All durable context must exist as files in the repository.

No critical knowledge may exist only in AI hidden state.

Separation by Lifecycle, Not Topic

Files are separated by volatility and longevity.

Mixing volatile and durable information is prohibited.

Event-Driven, Not Continuous

Reconciliation only occurs on defined events.

No per-command or constant polling behavior.

Cheap, Predictable Operations

Skill Init must run quickly and deterministically.

No large-scale rewrites or unbounded scans.

4. Memory Model
4.1 Memory File Roles
CLAUDE-activeContext.md

Role: Volatile working memory

Contains:

in-progress tasks

provisional assumptions

unresolved blockers

temporary notes

Must NOT contain:

finalized decisions

reusable patterns

long-term truths

Lifecycle: Ephemeral, scoped to a single soul purpose

CLAUDE-soul-purpose.md

Role: Governing objective definition

Definition:
The one question that must be answered by the current work

Properties:

Exactly one active soul purpose at a time

May be trivial or complex

Lifecycle: Updated when purpose changes or closes

CLAUDE-decisions.md

Role: Durable decision log (ADR-style)

Contains:

finalized architectural or design decisions

rationale and tradeoffs

Lifecycle: Append-only (decisions are superseded, not erased)

CLAUDE-patterns.md

Role: Reusable abstractions and conventions

Contains:

coding patterns

structural conventions

Lifecycle: Grows slowly, updated only when reuse is proven

CLAUDE-troubleshooting.md

Role: Known issues and validated fixes

Contains:

recurring problems

verified solutions

Lifecycle: Append-only

CLAUDE.md

Role: Governance contract for Claude

Contains:

explanation of context system

file roles and lifecycle rules

obligations for invoking Skill Init

Lifecycle: Changes rarely; not a working log

5. Active Context Lifecycle
Definition

Active context represents working memory, analogous to:

OS working sets

sprint context

incident logs

Rules

Active context is scoped to one soul purpose

It is expected to become outdated quickly

It must never be treated as historical truth

Clearing Rule

When a soul purpose is closed, active context must be harvested and cleared.

Clearing must occur via Skill Init reconciliation, never implicitly.

6. Soul Purpose Lifecycle
6.1 Authority Model

AI may suspect completion

AI may verify completion

AI may recommend closure

Only the user may close a soul purpose

AI must never hard-stop work.

6.2 Completion Protocol (Three-Stage)
Stage 1 — AI Suspicion (Non-Blocking)

Triggered when:

success criteria appear satisfied

no open TODOs remain

user language implies completion

Action:

Set internal possible_completion flag

No interruption, no file changes

Stage 2 — AI Preflight Check (Optional Agent)

Triggered when suspicion persists.

Agent evaluates:

stated soul purpose

expected artifacts

actual artifacts

unresolved gaps

Outputs one of:

clearly_incomplete

likely_complete

uncertain

No user interaction yet.

Stage 3 — User Confirmation (Authoritative)

Only for likely_complete or uncertain.

Prompt (non-blocking):

Close soul purpose

Continue current purpose

Redefine purpose

If user does nothing, work continues.

7. Event-Driven Reconciliation
7.1 Canonical Events

Skill Init reconciliation may run on:

Soul purpose started

Soul purpose closed (user-confirmed)

Non-trivial decision finalized

Reusable pattern identified

Blocker resolved

Manual Skill Init invocation

7.2 Reconciliation Behavior

When invoked, Skill Init must:

Scan context files relevant to the event

Promote volatile content to durable files if appropriate

Clear or reset active context when required

Update soul purpose state if changed

Avoid global rewrites

Reconciliation runs in audit mode, not rewrite mode.

8. Role of Skill Init vNext

Skill Init is responsible for:

enforcing lifecycle rules

reconciling state on events

preventing context drift

keeping memory coherent and minimal

Skill Init is not responsible for:

deciding what work to do

determining when work is finished

acting without user authority

9. Failure Modes Addressed

This design explicitly prevents:

Premature AI stopping

Infinite AI execution

Context rot

Redundant or ceremonial files

Hidden or lost intent

10. Success Criteria

Skill Init vNext is successful if:

Active context remains small and fresh

Durable files grow slowly and intentionally

Users trust the system without micromanaging it

Claude consistently reasons from explicit project state

The system works without constant user prompts

11. Implementation Notes (Non-Prescriptive)

Reconciliation should be fast and bounded

Event detection may be heuristic

Agents may be used for verification but never authority

All behavior must be explainable to the user

12. Summary

Skill Init vNext formalizes a project cognition lifecycle built on:

explicit memory

clear authority

bounded objectives

event-driven reconciliation

It does not reduce structure — it justifies it.

This specification defines the minimum rules required to make the system reliable, non-redundant, and generalizable.
