"""
FastAPI backend for Multi-Agent Dungeon (MAD).
"""

import os
import json
from typing import Optional, Dict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agents import PosterHostAgent, GuideAgent
from agents.ollama_service import OllamaService
from tts_service import TTSService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Dungeon API",
    description="Backend service for the MAD open house virtual environment",
    version="0.1.0"
)

# Add CORS middleware to allow Godot client to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Godot client origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load poster data
DATA_DIR = Path(__file__).parent / "data"
POSTERS_FILE = DATA_DIR / "posters.json"

posters_data = []
poster_agents: Dict[str, PosterHostAgent] = {}
guide_agent: Optional[GuideAgent] = None
ollama_service: Optional[OllamaService] = None
tts_service: Optional[TTSService] = None


def load_posters():
    """Load poster data from JSON file."""
    global posters_data
    try:
        with open(POSTERS_FILE, "r") as f:
            posters_data = json.load(f)
        print(f"Loaded {len(posters_data)} posters")
    except FileNotFoundError:
        print(f"Warning: {POSTERS_FILE} not found. Using empty poster list.")
        posters_data = []
    except json.JSONDecodeError as e:
        print(f"Error parsing {POSTERS_FILE}: {e}")
        posters_data = []


def initialize_agents():
    """Initialize all agents (poster hosts and guide)."""
    global poster_agents, guide_agent, ollama_service

    # Initialize Ollama service
    agent_mode = os.getenv("AGENT_MODE", "simple")
    if agent_mode == "ollama":
        ollama_service = OllamaService()
        print(f"Ollama service initialized (host: {ollama_service.host}, model: {ollama_service.model})")
    else:
        print("Running in simple mode (template-based responses)")

    # Create poster host agents
    for poster in posters_data:
        poster_id = poster["id"]
        agent = PosterHostAgent(
            agent_id=poster_id,
            name=f"Host for {poster['title']}",
            poster_data=poster,
            ollama_service=ollama_service,
        )
        poster_agents[poster_id] = agent

    # Create guide agent
    guide_agent = GuideAgent(
        agent_id="guide",
        name="Open House Guide",
        all_posters=posters_data,
        ollama_service=ollama_service,
    )

    print(f"Initialized {len(poster_agents)} poster host agents and 1 guide agent")


@app.on_event("startup")
async def startup_event():
    """Initialize data and agents on startup."""
    global tts_service

    load_posters()
    initialize_agents()

    # Initialize TTS service
    tts_service = TTSService(default_voice="en-US-female")
    print("✓ TTS service initialized")

    # Check Ollama connection if in ollama mode
    if ollama_service:
        is_connected = await ollama_service.check_connection()
        if is_connected:
            print("✓ Successfully connected to Ollama")
        else:
            print("✗ Could not connect to Ollama - will use simple mode as fallback")


# Request/Response models
class AgentRequest(BaseModel):
    """Request to interact with an agent."""
    agent_type: str  # "poster_host" or "guide"
    message: str
    poster_id: Optional[str] = None  # Required for poster_host agents
    session_id: Optional[str] = None  # For future session management


class AgentResponse(BaseModel):
    """Response from an agent."""
    reply: str
    agent_type: str
    poster_id: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Multi-Agent Dungeon API",
        "version": "0.1.0",
        "status": "running",
        "posters_loaded": len(posters_data),
        "agent_mode": os.getenv("AGENT_MODE", "simple"),
    }


@app.get("/posters")
async def list_posters():
    """List all available posters."""
    return {
        "count": len(posters_data),
        "posters": posters_data
    }


@app.get("/posters/{poster_id}")
async def get_poster(poster_id: str):
    """Get details for a specific poster."""
    poster = next((p for p in posters_data if p["id"] == poster_id), None)
    if not poster:
        raise HTTPException(status_code=404, detail=f"Poster {poster_id} not found")
    return poster


@app.post("/agent", response_model=AgentResponse)
async def interact_with_agent(request: AgentRequest):
    """
    Interact with an agent (poster host or guide).

    Args:
        request: AgentRequest with agent_type, message, and optional poster_id

    Returns:
        AgentResponse with the agent's reply
    """
    agent_type = request.agent_type.lower()

    # Route to appropriate agent
    if agent_type == "poster_host":
        if not request.poster_id:
            raise HTTPException(
                status_code=400,
                detail="poster_id is required for poster_host agents"
            )

        if request.poster_id not in poster_agents:
            raise HTTPException(
                status_code=404,
                detail=f"No agent found for poster {request.poster_id}"
            )

        agent = poster_agents[request.poster_id]
        reply = await agent.respond(request.message)

        return AgentResponse(
            reply=reply,
            agent_type="poster_host",
            poster_id=request.poster_id
        )

    elif agent_type == "guide":
        if not guide_agent:
            raise HTTPException(
                status_code=500,
                detail="Guide agent not initialized"
            )

        reply = await guide_agent.respond(request.message)

        return AgentResponse(
            reply=reply,
            agent_type="guide",
            poster_id=None
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agent_type: {agent_type}. Use 'poster_host' or 'guide'"
        )


@app.post("/tts")
async def text_to_speech(text: str, voice: Optional[str] = None):
    """
    Convert text to speech and return audio file.

    Args:
        text: Text to convert to speech
        voice: Voice to use (optional, uses default if not provided)

    Returns:
        MP3 audio file
    """
    if not tts_service:
        raise HTTPException(status_code=500, detail="TTS service not initialized")

    try:
        audio_file = await tts_service.generate_speech(text, voice=voice)
        return FileResponse(
            path=str(audio_file),
            media_type="audio/mpeg",
            filename="speech.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@app.get("/tts/voices")
async def list_tts_voices():
    """List available TTS voices."""
    if not tts_service:
        raise HTTPException(status_code=500, detail="TTS service not initialized")

    return {
        "default_voices": TTSService.VOICES,
        "default": tts_service.default_voice
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    ollama_status = "not_configured"
    if ollama_service:
        is_connected = await ollama_service.check_connection()
        ollama_status = "connected" if is_connected else "disconnected"

    tts_status = "initialized" if tts_service else "not_initialized"

    return {
        "status": "healthy",
        "posters_loaded": len(posters_data),
        "agents_initialized": len(poster_agents) + (1 if guide_agent else 0),
        "ollama_status": ollama_status,
        "tts_status": tts_status,
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print(f"Starting MAD API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
