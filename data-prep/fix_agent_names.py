#!/usr/bin/env python3
"""Fix agent names in Godot scene to match poster content."""

import json
import re
from pathlib import Path

# Load poster data
backend_file = Path(__file__).parent.parent / 'backend' / 'data' / 'posters.json'
with open(backend_file, 'r') as f:
    posters = {p['id']: p for p in json.load(f)}

# Generate appropriate agent names from poster titles
def generate_agent_name(title):
    """Generate a suitable agent name from poster title."""
    # Extract key topic from title
    title_lower = title.lower()

    if 'hpc' in title_lower or 'high-performance' in title_lower:
        return "HPC Researcher"
    elif 'graph neural' in title_lower or 'gnn' in title_lower:
        return "Graph Neural Network Researcher"
    elif 'language model' in title_lower or 'llm' in title_lower:
        return "Language Model Researcher"
    elif 'anomaly' in title_lower:
        return "Anomaly Detection Researcher"
    elif 'contiki' in title_lower or 'iot' in title_lower:
        return "IoT Systems Researcher"
    elif 'traffic' in title_lower:
        return "Traffic Prediction Researcher"
    else:
        # Generic fallback
        return "Research Scientist"

# Read scene file
scene_file = Path(__file__).parent.parent / 'client-godot' / 'scenes' / 'environment' / 'main.tscn'
with open(scene_file, 'r') as f:
    content = f.read()

# Update agent names for each booth
for poster_id, poster in posters.items():
    # Extract booth number from poster_id (e.g., "poster_001" -> 1)
    booth_num = int(poster_id.split('_')[1])
    booth_name = f"PosterBooth{booth_num}"

    # Generate new agent name
    new_agent_name = generate_agent_name(poster['title'])

    # Find and replace the agent_name line for this booth
    pattern = rf'(\[node name="{booth_name}"[^\[]*?agent_name = ")[^"]*(")'
    replacement = rf'\1{new_agent_name}\2'

    old_content = content
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if content != old_content:
        print(f"✓ Updated {booth_name}: {new_agent_name}")

# Write back
with open(scene_file, 'w') as f:
    f.write(content)

print(f"\n✓ Updated {scene_file}")
print("Agent names now match poster content!")
