---
name: odex_execution_engine
description: |
  ODEX Execution Engine — a real AI-powered build pipeline. Takes user prompt, triggers a full pipeline, executes all stages, and produces real output (file tree, code files, system structure, preview instructions). Behaves as an autonomous AI software engineer, not a checklist.
---

# ODEX_EXECUTION_ENGINE

## Overview
This skill is a full execution pipeline, not a checklist. It orchestrates all stages of the ODEX engineering process, transforming user prompts into real, working systems.

## Pipeline Controller
- Receives user prompt
- Routes through all pipeline stages
- Assigns tasks to AI cores
- Handles retries, error recovery, and human-in-the-loop review
- Produces deployable output

## Pipeline Stages
1. **Input Stage**
   - Capture user intent
   - Preprocess context
2. **Planning Stage**
   - Call AI Pilot (C-02)
   - Break into tasks
3. **Architecture Stage**
   - Generate system design (C-06)
   - DB schema, API map
4. **Build Stage**
   - Call builder cores (C-07)
   - Generate files, create structure
5. **Debug Stage**
   - Detect errors (C-08)
   - Auto fix, retry loop
6. **Test Stage**
   - Run tests (C-09)
   - Validate system
7. **Human Loop Stage**
   - Allow review, override, inject changes
8. **Deploy Stage**
   - Package system (C-15)
   - Prepare runtime, generate preview
9. **Learn Stage**
   - Capture user edits, update system memory

## Stage Logic
- Each stage calls mapped core (see cores.md)
- Orchestrator manages flow, retries, and worker assignment
- Human loop enables manual intervention and override

## Output
- File tree
- Code files
- System structure
- Preview instructions

## Usage
- "Build a REST API for inventory management."
- "Generate a web app with login and dashboard."
- "Create a database-backed backend and deploy preview."

## Related Files
- pipeline.md — Stage definitions
- cores.md — Core mapping
- orchestrator.md — Pipeline logic
- human_loop.md — Human-in-the-loop interface
- templates/ — System templates (backend, frontend, db)

## Final Rule
This skill acts as a real AI software engineer. It does not provide a checklist or documentation — it executes, builds, and delivers working systems.
