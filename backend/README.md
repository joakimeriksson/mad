# MAD Backend - Agent Service

Python FastAPI backend for the Multi-Agent Dungeon open house virtual environment.

## Features

- **Poster Host Agents**: One agent per research poster, knowledgeable about specific research
- **Guide Agent**: Helps visitors navigate and find posters based on interests
- **Dual Mode**: Supports both Ollama (LLM-based) and simple (template-based) responses
- **RESTful API**: Clean HTTP endpoints for Godot client integration

## Setup

### 1. Install Pixi (Recommended)

Pixi is a modern package manager that provides better dependency management:

```bash
# Install pixi (https://pixi.sh)
curl -fsSL https://pixi.sh/install.sh | bash

# Or on macOS with Homebrew
brew install pixi
```

### 2. Install Dependencies

**Option A: Using Pixi (Recommended)**

```bash
cd backend

# Install all dependencies and create environment
pixi install

# That's it! Pixi manages everything.
```

**Option B: Using pip (Alternative)**

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```
# For Ollama-based agents (requires Ollama running)
AGENT_MODE=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Or for simple template-based agents (no Ollama needed)
AGENT_MODE=simple
```

### 4. Install Ollama (Optional)

If you want LLM-powered agents:

1. Install Ollama: https://ollama.ai/download
2. Pull a model: `ollama pull llama2` (or llama3, mistral, etc.)
3. Verify it's running: `ollama list`

### 5. Run the Server

**Using Pixi (Recommended)**

```bash
# Start in development mode with auto-reload
pixi run dev

# Or start in production mode
pixi run start
```

**Using Python directly**

```bash
python app.py
```

Or with uvicorn:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Quick Commands with Pixi

```bash
# Run tests
pixi run test

# Check API health
pixi run health

# List posters
pixi run posters

# Run in dev mode with auto-reload
pixi run dev
```

## API Endpoints

### GET /
Basic API information and status

### GET /posters
List all available posters with metadata

### GET /posters/{poster_id}
Get details for a specific poster

### POST /agent
Interact with an agent

**Request body:**
```json
{
  "agent_type": "poster_host",  // or "guide"
  "message": "What is this research about?",
  "poster_id": "poster_001"  // required for poster_host
}
```

**Response:**
```json
{
  "reply": "This research explores...",
  "agent_type": "poster_host",
  "poster_id": "poster_001"
}
```

### GET /health
Health check with Ollama connection status

## Testing

### Test with curl

```bash
# Check API status
curl http://localhost:8000/

# List posters
curl http://localhost:8000/posters

# Talk to guide agent
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "guide",
    "message": "What posters do you have about robotics?"
  }'

# Talk to poster host
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "poster_host",
    "message": "Tell me about this research",
    "poster_id": "poster_001"
  }'
```

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── data/
│   └── posters.json   # Poster metadata
└── agents/
    ├── __init__.py
    ├── base.py        # Base agent class
    ├── poster_host.py # Poster host agent
    ├── guide.py       # Guide agent
    └── ollama_service.py  # Ollama LLM wrapper
```

## Agent Modes

### Simple Mode (Default Fallback)
- Template-based responses
- Pattern matching on keywords
- Uses FAQ data from posters.json
- Works without any external dependencies
- Good for testing and offline development

### Ollama Mode (LLM-Powered)
- Natural language understanding
- Context-aware conversations
- More flexible responses
- Requires Ollama running locally
- Automatically falls back to simple mode if Ollama is unavailable

## Adding New Posters

Edit `data/posters.json` and add a new entry:

```json
{
  "id": "poster_006",
  "title": "Your Research Title",
  "authors": ["Author Name"],
  "tags": ["tag1", "tag2"],
  "room": "room_1",
  "booth_id": "booth_6",
  "abstract": "Research abstract...",
  "poster_image": "res://assets/posters/poster_006.png",
  "faq": [
    {
      "question": "Common question?",
      "answer": "Answer here"
    }
  ]
}
```

Restart the server to load new posters.
