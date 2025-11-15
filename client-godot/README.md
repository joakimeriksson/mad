# MAD Godot Client - 3D Virtual Open House

Godot 4.x client for the Multi-Agent Dungeon (MAD) open house virtual environment.

## Features

- **First-Person Movement**: WASD + mouse look controls
- **Interactive Environment**: Corridor and rooms with poster booths
- **Agent Dialogue System**: Chat UI for talking with AI agents
- **HTTP Integration**: Connects to Python backend for agent responses
- **5 Research Posters**: Each with a dedicated expert agent
- **Guide Kiosk**: Helps navigate and find posters by topic

## Requirements

- **Godot 4.3** or later
- **MAD Backend** running on `http://localhost:8000` (see `../backend/README.md`)

## Project Structure

```
client-godot/
├── project.godot          # Main project configuration
├── scenes/
│   ├── environment/
│   │   └── main.tscn     # Main game scene (start here)
│   ├── player/
│   │   └── player.tscn   # Player character
│   ├── ui/
│   │   └── dialogue_ui.tscn  # Chat interface
│   └── interactables/
│       ├── poster_booth.tscn  # Poster booth prefab
│       └── guide_kiosk.tscn   # Guide kiosk prefab
├── scripts/
│   ├── player_controller.gd   # Player movement and look
│   ├── agent_service.gd       # HTTP client for backend
│   ├── dialogue_ui.gd         # Chat UI logic
│   ├── interactable.gd        # Base interactable class
│   └── game_controller.gd     # Main game coordinator
└── assets/
    ├── posters/          # Poster images (add your own)
    ├── models/           # 3D models
    └── materials/        # Materials and textures
```

## How to Run

### 1. Start the Backend

First, make sure the MAD backend is running:

```bash
cd ../backend
python app.py
```

You should see:
```
Starting MAD API server on 0.0.0.0:8000
Loaded 5 posters
Running in simple mode (template-based responses)
```

### 2. Open in Godot

1. Launch **Godot 4.3** (or later)
2. Click **Import**
3. Navigate to `client-godot/project.godot`
4. Click **Import & Edit**

### 3. Run the Game

- Press **F5** or click the **Play** button
- The main scene will load automatically

## Controls

| Key | Action |
|-----|--------|
| **W A S D** | Move forward/left/backward/right |
| **Mouse** | Look around |
| **E** | Interact with poster booths / guide kiosk |
| **ESC** | Close dialogue / Release mouse |
| **Space** | Jump |

## Gameplay

1. **Start at the entrance** - You spawn in the corridor near the guide kiosk
2. **Talk to the Guide** - Walk up to the guide kiosk and press **E** to ask about posters
3. **Explore poster booths** - Walk around to find the 5 research posters
4. **Interact with posters** - Get close to a booth and press **E** to talk to the researcher
5. **Chat in the UI** - Type questions and get responses from the agents

## Environment Layout

```
        [Room 1]
            |
    [=====Corridor=====]
            |
        [Room 2]

Corridor: 4 poster booths + guide kiosk
Room 1: Additional poster space
Room 2: Additional poster space
```

## Poster Locations

1. **Guide Kiosk** - Center of corridor (near entrance)
2. **Edge AI for Autonomous Robotics** - Corridor, left side
3. **Federated Learning for Healthcare** - Corridor, left side
4. **Quantum-Resistant Cryptography** - Corridor, right side
5. **Human-Robot Collaboration** - Corridor, left side
6. **Sustainable Data Centers** - Corridor, right side

## Customization

### Adding Poster Images

1. Export your poster as PNG (recommended: 1920x1080 or similar)
2. Place in `assets/posters/`
3. In Godot, select a PosterBooth node
4. Find the PosterMesh → Material
5. Assign your texture to the material's albedo

### Changing API URL

Edit `scenes/environment/main.tscn` → AgentService → `api_url` property

Or edit `scripts/agent_service.gd`:
```gdscript
@export var api_url: String = "http://localhost:8000"
```

### Adding More Posters

1. Add poster data to `../backend/data/posters.json`
2. Restart the backend
3. In Godot, duplicate a PosterBooth scene
4. Update its properties:
   - `agent_name`: Researcher name
   - `poster_id`: Must match ID in posters.json
   - `Label3D.text`: Poster title

## Troubleshooting

### "Connection failed" errors

- Make sure the backend is running on `http://localhost:8000`
- Check the Godot console for error messages
- Test backend: `curl http://localhost:8000/health`

### Can't interact with objects

- Make sure you're close enough (within ~2 meters)
- Check that collision layers are set correctly
- Player should be on Layer 3, Interactables on Layer 2

### Mouse not captured

- Press ESC to toggle mouse capture
- Mouse should auto-capture on game start

### Dialogue UI not showing

- Check that DialogueUI node exists in main scene
- Verify agent_service_path is set correctly
- Check console for script errors

## Development

### Scene Organization

- **main.tscn**: Main scene, contains environment and game logic
- **player.tscn**: Reusable player prefab
- **poster_booth.tscn**: Reusable booth prefab (instance and customize)
- **guide_kiosk.tscn**: Guide agent kiosk
- **dialogue_ui.tscn**: Chat interface overlay

### Script Architecture

- **GameController**: Coordinates all systems
- **PlayerController**: Handles movement and input
- **AgentService**: HTTP client (singleton-like)
- **DialogueUI**: Manages chat interface
- **Interactable**: Base class for interactive objects

## Future Improvements

- [ ] Better 3D models for booths and kiosks
- [ ] Poster textures with actual research content
- [ ] Minimap for navigation
- [ ] Sound effects and ambient audio
- [ ] Multiple rooms with themed areas
- [ ] NPC avatars for agents
- [ ] Voice synthesis for agent responses
- [ ] Multiplayer support

## Credits

Built with **Godot 4.3** as part of the **Multi-Agent Dungeon (MAD)** project.

Backend: FastAPI + Python agents (Ollama-powered or template-based)
