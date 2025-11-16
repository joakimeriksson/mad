#!/usr/bin/env python3
"""Update Godot scene with correct poster titles from backend JSON."""

import json
from pathlib import Path

# Load poster data
backend_file = Path(__file__).parent.parent / 'backend' / 'data' / 'posters.json'
with open(backend_file, 'r') as f:
    posters = json.load(f)

# Create title mapping
poster_titles = {p['id']: p['title'] for p in posters}

print("Poster titles to update:")
for poster_id, title in poster_titles.items():
    print(f"  {poster_id}: {title}")

# Read scene file
scene_file = Path(__file__).parent.parent / 'client-godot' / 'scenes' / 'environment' / 'main.tscn'
with open(scene_file, 'r') as f:
    lines = f.readlines()

# Update titles
updated_lines = []
current_booth = None

for i, line in enumerate(lines):
    # Detect which booth we're in
    if '[node name="PosterBooth' in line:
        # Extract booth number
        import re
        match = re.search(r'PosterBooth(\d+)', line)
        if match:
            booth_num = int(match.group(1))
            current_booth = f"poster_{booth_num:03d}"

    # Update Label3D text if we're in a booth
    if current_booth and 'text = ' in line and 'Label3D' in lines[i-1]:
        if current_booth in poster_titles:
            title = poster_titles[current_booth]
            # Replace the text
            indent = line[:line.index('text')]
            line = f'{indent}text = "{title}"\n'
            print(f"Updated {current_booth} label")

    updated_lines.append(line)

# Write back
with open(scene_file, 'w') as f:
    f.writelines(updated_lines)

print(f"\n✓ Updated {scene_file}")
print("Scene file updated with correct poster titles!")
