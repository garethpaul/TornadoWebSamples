# Tornado Transport Guide Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Separate Comet and WebSocket operating boundaries in the README and reconcile the related completed roadmap items with executable documentation contracts.

**Architecture:** Preserve both tutorial implementations exactly. Add a fail-closed static contract for supported versions, transport-specific validation, broadcast coverage, caveats, and roadmap history; then restructure README guidance around those verified facts.

**Tech Stack:** Markdown, Python 3 static contracts, pytest, Tornado 6.5.7, GNU Make

---

## Status: Completed

### Task 1: Add The Documentation Contract

**Files:**
- Modify: `scripts/check_docs_plans.py`
- Test: `scripts/check_docs_plans.py`

**Step 1: Write the failing test**

Add required README phrases for Python/Tornado support, distinct Comet and
WebSocket sections, transport-specific input limits, broadcast tests, and
production caveats. Require the roadmap and change history to record the
reconciliation.

**Step 2: Run test to verify it fails**

Run: `python3 scripts/check_docs_plans.py`

Expected: FAIL because the existing README mixes transport guidance and the
roadmap still lists completed items.

### Task 2: Write The Transport Guide

**Files:**
- Modify: `README.md`
- Modify: `VISION.md`
- Modify: `CHANGES.md`

**Step 1: Write minimal documentation**

Replace generated inventory with actual source/test surfaces, state supported
Python and Tornado versions, and add separate Comet and WebSocket sections with
input, admission, delivery-failure, browser, and production boundaries.

**Step 2: Run focused contracts**

Run: `python3 scripts/check_docs_plans.py`

Expected: PASS.

### Task 3: Prove Drift Fails Closed

**Files:**
- Test: `scripts/check_docs_plans.py`

**Step 1: Apply hostile mutations**

Mutate supported versions, each transport heading, body/frame limits, semantic
message limits, XSRF/origin boundaries, admission limits, timeout/close codes,
broadcast-test evidence, production caveats, roadmap history, and plan status.

**Step 2: Verify each mutation fails**

Run: `python3 scripts/check_docs_plans.py` after each mutation.

Expected: every mutation is rejected.

### Task 4: Run The Full Gate

**Files:**
- Verify: `Makefile`

**Step 1: Install pinned dependencies**

Run: `python3 -m pip install -r requirements.txt -r test-requirements.txt`

Expected: exact pinned dependencies install.

**Step 2: Run repository and external gates**

Run: `make check`

Run: `cd "$(mktemp -d)" && make -f /absolute/path/to/Makefile check`

Expected: tests, contracts, audits, and both Make invocation modes pass.

### Task 5: Commit And Ship

**Files:**
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-26-tornado-transport-guide.md`

**Step 1: Record exact validation**

Add final test, mutation, audit, and hosted-check evidence.

**Step 2: Commit**

```bash
git add README.md VISION.md CHANGES.md scripts/check_docs_plans.py docs/plans/2026-06-26-tornado-transport-guide.md
git commit -m "docs: separate Tornado transport guidance"
```

## Results

- Replaced the stale inventory and mixed verification notes with separate,
  source-backed Comet and WebSocket operating guides.
- Retired four completed roadmap items while preserving one explicit priority
  to keep transport-specific setup, validation, broadcast, and caveat guidance
  synchronized with the implementation.
- Rejected 21 hostile documentation mutations covering versions, sections,
  limits, delivery behavior, caveats, roadmap history, and plan completion.
- Passed `make check` with the exact pinned dependencies in clean CPython 3.12
  and 3.14 containers: 45 tests, all 32 existing contract mutations, `pip
  check`, and both dependency audits. The external-path Make gate also passed
  on CPython 3.12.
