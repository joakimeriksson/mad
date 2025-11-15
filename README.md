# MAD - Multi-Agent Dungeon

A 3D virtual open house environment where visitors can explore research posters and interact with AI agents that explain the research.

## Overview

**MAD (Multi-Agent Dungeon)** is a proof-of-concept for creating immersive virtual exhibitions with intelligent agent guides. Built for the RISE Computer Science open house, it demonstrates how AI agents can enhance virtual events by providing personalized, interactive experiences.

### Key Features

- 🎮 **3D Virtual Environment** - Walk through a virtual office building with corridors and exhibition rooms
- 🤖 **AI-Powered Agents** - Talk to research experts and a helpful guide agent
- 📊 **Interactive Posters** - 5 research posters with detailed metadata
- 💬 **Natural Dialogue** - Chat interface for conversations with agents
- 🔌 **Modular Architecture** - Easy to add new posters and customize content
- 🌐 **Local LLM Support** - Works with Ollama or uses simple template responses

## Architecture

### Components

```
┌─────────────────────────────────────────┐
│     Godot 4.x Client (3D Frontend)      │
│  ┌──────────┐  ┌─────────────────────┐  │
│  │  Player  │  │   Dialogue UI       │  │
│  │ Movement │  │   (Chat Interface)  │  │
│  └──────────┘  └─────────────────────┘  │
│  ┌──────────────────────────────────┐   │
│  │   Poster Booths & Guide Kiosk    │   │
│  └──────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │ HTTP
                  ▼
┌─────────────────────────────────────────┐
│   FastAPI Backend (Agent Service)       │
│  ┌────────────┐    ┌─────────────────┐  │
│  │ Poster     │    │  Guide Agent    │  │
│  │ Host       │    │  (Navigation)   │  │
│  │ Agents (5) │    │                 │  │
│  └────────────┘    └─────────────────┘  │
│  ┌─────────────────────────────────┐    │
│  │    Ollama Service (Optional)    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: Godot 4.3 (GDScript)
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **AI/LLM**: Ollama (optional), template-based fallback
- **Data**: JSON-based poster metadata

## Quick Start

### Prerequisites

- Python 3.11+
- Godot 4.3+ (download from https://godotengine.org)
- (Optional) Ollama for LLM-powered agents

### 1. Start the Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

The API will be available at `http://localhost:8000`

### 2. Run the Godot Client

```bash
# Open Godot 4.3
# Click Import → Navigate to client-godot/project.godot
# Press F5 to run
```

### 3. Explore the Virtual Open House

- Walk around with **WASD**
- Look with **mouse**
- Press **E** near poster booths or the guide kiosk to interact
- Chat with agents in the dialogue UI

## Project Structure

```
mad/
├── README.md              # This file
├── PLAN.md               # Detailed project plan
├── CLAUDE.md             # AI coding assistant instructions
│
├── backend/              # Python FastAPI agent service
│   ├── app.py           # Main API server
│   ├── agents/          # Agent implementations
│   │   ├── base.py
│   │   ├── poster_host.py
│   │   ├── guide.py
│   │   └── ollama_service.py
│   ├── data/
│   │   └── posters.json  # Poster metadata
│   ├── requirements.txt
│   ├── test_api.py
│   └── README.md
│
├── client-godot/         # Godot 4.x 3D client
│   ├── project.godot    # Godot project config
│   ├── scenes/          # Scene files
│   │   ├── environment/main.tscn
│   │   ├── player/player.tscn
│   │   ├── ui/dialogue_ui.tscn
│   │   └── interactables/
│   ├── scripts/         # GDScript files
│   │   ├── player_controller.gd
│   │   ├── agent_service.gd
│   │   ├── dialogue_ui.gd
│   │   ├── interactable.gd
│   │   └── game_controller.gd
│   ├── assets/          # 3D models, textures, posters
│   └── README.md
│
└── data-prep/           # (Future) Data preparation scripts
```

## Research Posters

The demo includes 5 research posters:

1. **Edge AI for Autonomous Robotics** - Efficient deep learning for edge devices
2. **Federated Learning for Privacy-Preserving Healthcare** - Collaborative ML without sharing data
3. **Quantum-Resistant Cryptography for IoT** - Post-quantum security for sensors
4. **Human-Robot Collaboration in Manufacturing** - Safe shared workspaces
5. **Sustainable Data Centers** - AI-driven cooling optimization

Each poster has:
- Title, authors, abstract
- Tags for topic-based search
- FAQ with common questions
- A dedicated agent that can discuss the research

## Agent Types

### Poster Host Agents

One agent per poster that acts as the research expert:
- Answers questions about the specific research
- Grounded in poster metadata (abstract, tags, FAQ)
- Can discuss methodology, results, applications
- Powered by Ollama LLM or template-based responses

### Guide Agent

A navigation assistant located at the guide kiosk:
- Helps find posters by topic (AI, robotics, security, healthcare, sustainability)
- Provides directions to rooms and booths
- Recommends posters based on visitor interests
- Knows about all posters in the exhibition

## Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# Use Ollama for LLM-powered agents
AGENT_MODE=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Or use simple template-based responses
AGENT_MODE=simple
```

### Adding New Posters

1. Add entry to `backend/data/posters.json`:

```json
{
  "id": "poster_006",
  "title": "Your Research Title",
  "authors": ["Author Names"],
  "tags": ["topic1", "topic2"],
  "room": "corridor",
  "booth_id": "booth_6",
  "abstract": "Research description...",
  "poster_image": "res://assets/posters/poster_006.png",
  "faq": [
    {
      "question": "Common question?",
      "answer": "Answer here"
    }
  ]
}
```

2. Restart backend
3. Add booth in Godot (duplicate existing PosterBooth scene)
4. Update booth properties with new poster_id

## Development Roadmap

### MVP (Current Status) ✅

- [x] Python FastAPI backend with agent system
- [x] Poster host and guide agents
- [x] Godot 4.x project structure
- [x] First-person player controller
- [x] Basic 3D environment (corridor + rooms)
- [x] Poster booth and guide kiosk scenes
- [x] Dialogue UI system
- [x] HTTP communication between client and backend

### Phase 2 (Future)

- [ ] Better 3D models for booths
- [ ] Actual poster textures from research PDFs
- [ ] Enhanced environment (lighting, materials, decorations)
- [ ] Minimap and navigation aids
- [ ] Sound effects and ambient audio
- [ ] Agent avatars (3D characters)

### Phase 3 (Future)

- [ ] Multi-room building with themed areas
- [ ] Dynamic poster loading from CMS
- [ ] Analytics (which posters get visited)
- [ ] VR support
- [ ] Multiplayer networking
- [ ] Voice synthesis for agents
- [ ] Integration with real RISE poster database

## Testing

### Backend Tests

```bash
cd backend

# Start server
python app.py

# In another terminal, run tests
python test_api.py

# Or test manually with curl
curl http://localhost:8000/health
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "guide", "message": "What do you have about robotics?"}'
```

### Godot Testing

1. Open project in Godot
2. Press F5 to run
3. Test player movement (WASD)
4. Test interactions (E key near booths)
5. Test dialogue UI (type messages, get responses)

## Troubleshooting

### Backend won't start

- Check Python version: `python --version` (need 3.11+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is available: `lsof -i :8000`

### Godot can't connect to backend

- Verify backend is running: `curl http://localhost:8000/health`
- Check Godot console for error messages
- Verify AgentService `api_url` is set to `http://localhost:8000`

### Ollama not working

- Install Ollama: https://ollama.ai/download
- Pull a model: `ollama pull llama2`
- Verify it's running: `ollama list`
- Set `AGENT_MODE=ollama` in `backend/.env`
- Fallback: Use `AGENT_MODE=simple` (no Ollama needed)

## Contributing

This is a research prototype. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Use Cases

- **Virtual Open Houses** - Host research exhibitions online
- **Museum Exhibits** - Interactive guides for virtual museums
- **Educational Demos** - Teaching environments with AI tutors
- **Conference Posters** - Virtual poster sessions with Q&A
- **Product Showcases** - Virtual showrooms with AI sales assistants

## License

[Specify your license here]

## Acknowledgments

- Built with **Godot Engine** (https://godotengine.org)
- Powered by **FastAPI** (https://fastapi.tiangolo.com)
- LLM support via **Ollama** (https://ollama.ai)
- Developed for **RISE Computer Science**

## Contact

[Add contact information here]

---

**MAD - Where virtual spaces meet intelligent agents** 🎮🤖
