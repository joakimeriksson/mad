# Multi-Agent Dungeon (MAD) – Open House MVP Plan

## 0. Summary

We are building a **Multi-Agent Dungeon (MAD)**: a 3D virtual environment in Godot where visitors can explore a stylised replica of the RISE Computer Science open house. 

For the **first MVP**, the focus is:

- Single-player experience (no networking).
- One corridor + 1–2 rooms.
- 3–5 poster booths showing real poster content.
- A **Guide kiosk agent** that helps you find demos.
- **Poster host agents** that explain each poster and answer questions.
- Simple Python backend with an `/agent` endpoint that uses poster/demo metadata + an LLM.

This document describes scope, architecture, milestones, and concrete tasks so that agentic coding tools (Claude, etc.) can help implement it.

---

## 1. Goals

1. **Demonstrate** a working end-to-end pipeline from:
   - Poster metadata → 3D environment → interactive agents.
2. **Create a reusable framework** where a future open house only requires updating data (posters, booths, rooms), not rewriting code.
3. **Use agentic coding** to:
   - Scaffold Godot project structure.
   - Implement clean, testable backend services.
   - Automate data preparation (poster JSON/YAML, FAQs).

---

## 2. Scope of the MVP

### 2.1. Functional scope

**Player**

- Walk around a simple 3D environment (corridor + 1–2 rooms).
- Interact with:
  - Poster booths
  - One guide kiosk

**Booths & posters**

- 3–5 booths with:
  - Visible poster textures (PNG/JPG).
  - Basic label (poster title above/below the poster).
- Interaction:
  - When close and pressing `E`, a dialogue UI opens.

**Agents**

- **Poster host agent**
  - One host per poster.
  - Answers: “What is this poster about?”, “How does this relate to X?”
  - Grounded in poster metadata: title, abstract, tags, simple FAQ.

- **Guide agent (kiosk)**
  - Answers: “Where are the robotics demos?”, “What should I visit for Edge AI?”
  - Uses tags and room assignments to suggest demos.

**Backend**

- Simple Python HTTP API:
  - `POST /agent`  
    Request: `{ agent_type, message, poster_id? }`  
    Response: `{ reply }`
- Reads poster & booth metadata (JSON/YAML).
- Wraps an LLM or simple heuristic logic (LLM integration can be swapped later).

**Non-goals for MVP**

- Multi-user networking.
- VR.
- Complex NPC movement and pathfinding.
- Full building model; we only need a recognisable slice.

---

## 3. Architecture Overview

### 3.1. High-level components

1. **Godot Client**
   - 3D world (corridor + rooms).
   - Player controller (WASD + mouse).
   - Poster booths & guide kiosk scenes.
   - Dialogue UI.
   - HTTP client to talk to backend.

2. **Agent Backend (Python)**
   - FastAPI (or similar) service exposing `/agent`.
   - Loads `posters.json` (and later `booths.json`).
   - Agent logic:
     - Poster host: answers using specific poster metadata.
     - Guide: answers using tags across all posters.

3. **Content & Data**
   - `posters.json`: list/dict of posters.
   - `booths.json`: optional, describes where booths are placed and which poster they host.
   - Poster images: PNGs for rendering in Godot.

### 3.2. Suggested repository structure

Either a monorepo:

```text
mad/
  plan-mad.md
  claude.md

  client-godot/        # Godot project
    project.godot
    scenes/
    scripts/
    assets/
    config/

  backend/             # Python agent backend
    app.py
    posters.json
    requirements.txt / pyproject.toml

  data-prep/           # Optional helpers for poster data
    extract_posters.py
    generate_faqs.py
