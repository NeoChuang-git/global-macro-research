# Agent Instructions

Guidelines and conventions for AI coding agents working in this repository.

## Agent skills

### Issue tracker

Issues and specs for this repo live as GitHub issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Triage roles map to canonical GitHub labels (`needs-triage`, `ready-for-agent`, etc.). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`CONTEXT.md` and `docs/adr/` at repo root). See `docs/agents/domain.md`.

## Standard Engineering Pipeline

When developing new features, modules, or major refactors, the Agent Harness executes the following canonical workflow sequentially:

1. **Phase 1: Grill-me (`/grill-me`)**
   - Interview the user across the decision tree frontier until all architectural constraints, seams, and failure modes are settled.
   - Update `CONTEXT.md` inline with domain language and record ADRs in `docs/adr/` where justified.

2. **Phase 2: Specification Synthesis (`/to-spec`)**
   - Synthesize the settled conversation into an actionable specification (Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions).
   - Publish the specification to GitHub Issues labelled `ready-for-agent`.

3. **Phase 3: Ticket Graph (`/to-tickets`)**
   - Decompose the specification into discrete, dependency-tracked implementation tickets on GitHub.

4. **Phase 4: Implementation (`/implement-spec` & `/tdd`)**
   - Branch off `main` (or dedicated feature branch).
   - Implement ticket-by-ticket using Test-Driven Development (red-green-refactor).
   - Maintain 100% passing tests throughout.

5. **Phase 5: Code Review & Verification (`/code-review`)**
   - Run parallel two-axis review: Standards (repo conventions + Fowler smell baseline) and Spec (requirement completeness & zero scope creep).
   - Resolve any identified issues before declaring completion.

