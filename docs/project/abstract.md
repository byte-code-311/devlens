# DevLens: Evidence-Backed Bug Triage

## Abstract

Software teams receive bug reports that often describe a symptom without identifying the code path or tests that should be inspected. DevLens is a local-first full-stack application that organizes bug reports and retrieves relevant snippets from a curated sample codebase and related issue notes. It produces a triage summary, possible investigation leads, and regression-test ideas with explicit references to the evidence used. A deterministic baseline mode works without external credentials; an optional language-model provider returns structured suggestions that are validated against retrieved evidence identifiers. The system uses a React and TypeScript interface, a FastAPI backend, and SQLite storage. The project demonstrates API design, relational persistence, search, structured AI integration, error handling, and evidence provenance. Its goal is to support investigation and learning, not to claim an automated or confirmed root-cause diagnosis.

## Problem statement

Bug reports frequently lack direct links to relevant code and regression tests. Developers must search manually, and ungrounded AI answers can make investigation harder when their sources are unclear.

## Proposed solution

DevLens stores structured bug reports, searches a small indexed corpus, and displays triage suggestions beside the exact retrieved snippets that support them. When evidence is insufficient, it states that limitation and withholds root-cause hypotheses.

## Objectives

- Build a usable report creation and history workflow.
- Implement a REST API and persistent SQLite data model.
- Retrieve code and issue evidence with stable source references.
- Provide both no-key baseline and optional AI-assisted triage modes.
- Validate model citations against evidence actually retrieved for each run.
- Collect user feedback and provide a reproducible local demonstration.

## Keywords

Bug triage, full-stack development, information retrieval, structured AI output, evidence provenance, FastAPI, React, SQLite.
