---

## 2. `claude.md` for agentic coding

This is tailored so that an agent (Claude or similar) understands the project, stack, and how to behave when helping you code for MAD.

```markdown
# Project: Multi-Agent Dungeon (MAD) – Open House MVP

You are an AI coding assistant working on **Multi-Agent Dungeon (MAD)**, a 3D multi-agent environment built with **Godot** (client) and **Python** (backend).

The first concrete objective is to deliver an MVP: a **single-player** virtual open house for RISE Computer Science, with a small 3D environment, interactive poster booths, and simple agents that answer questions.

---

## 1. High-Level System Overview

### 1.1. Godot Client (3D Frontend)

- Engine: **Godot 4.x**.
- Language: **GDScript** (preferred) or optionally C#, but assume GDScript unless instructed otherwise.
- Core responsibilities:
  - Render a small 3D level (corridor + 1–2 rooms).
  - Handle player movement and camera controls (WASD + mouse).
  - Display poster booths and a guide kiosk.
  - Show an in-game dialogue UI for conversations with agents.
  - Communicate with the agent backend over HTTP.

### 1.2. Backend (Agent Service)

- Language: **Python**.
- Framework: **FastAPI** (default assumption unless repo states otherwise).
- Responsibilities:
  - Expose a minimal HTTP API: `POST /agent`.
  - Load poster/demo metadata from JSON or YAML (`posters.json` at minimum).
  - Implement two main agent roles:
    - `poster_host`: answers about a specific poster.
    - `guide`: helps visitors find interesting posters/demos based on topics/tags.
  - Optionally integrate an LLM; otherwise use template-based heuristics.

### 1.3. Content & Data

- Poster metadata stored in `posters.json` (or `.yaml`), including:
  - `id`
  - `title`
  - `authors`
  - `tags`
  - `abstract`
  - `poster_image` path for Godot.
- Later we may add: `faq`, `room`, `booth_id`, etc.

---

## 2. Repositories & Structure

Assume a monorepo similar to:

```text
mad/
  plan-mad.md
  claude.md

  client-godot/
    project.godot
    scenes/
    scripts/
    assets/
    config/

  backend/
    app.py
    posters.json
    pyproject.toml or requirements.txt

  data-prep/
    extract_posters.py
    generate_faqs.py
