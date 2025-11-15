"""
Update main.tscn to include poster materials and correct titles.
Run this to update the Godot scene file directly.
"""

import json
from pathlib import Path
import re


def load_poster_data():
    """Load poster data from backend."""
    backend_data = Path(__file__).parent.parent / "backend" / "data" / "posters.json"
    with open(backend_data, 'r') as f:
        return json.load(f)


def update_main_scene():
    """Update the main.tscn file with poster materials and titles."""

    scene_file = Path(__file__).parent.parent / "client-godot" / "scenes" / "environment" / "main.tscn"

    print(f"Reading {scene_file}")
    with open(scene_file, 'r') as f:
        content = f.read()

    # Load poster data
    posters = load_poster_data()
    poster_dict = {p['id']: p for p in posters[:5]}  # First 5 posters

    print(f"Loaded {len(poster_dict)} posters from backend")

    # Update titles (they're already correct in the file, but let's verify)
    for i in range(1, 6):
        poster_id = f"poster_{i:03d}"
        if poster_id in poster_dict:
            title = poster_dict[poster_id]['title']
            # Find and replace the Label3D text for this booth
            pattern = rf'(\[node name="Label3D" parent="Interactables/PosterBooth{i}" index="4"\]\s*text = ")[^"]*(")'
            replacement = rf'\1{title}\2'
            content = re.sub(pattern, replacement, content)
            print(f"Updated PosterBooth{i} title: {title}")

    # Write back
    with open(scene_file, 'w') as f:
        f.write(content)

    print(f"\n✓ Updated {scene_file}")
    print("\nNOTE: Materials will be applied when you run the Godot script.")
    print("The scene file has been updated with correct titles.")
    print("\nNext steps:")
    print("1. Open Godot")
    print("2. Open scenes/environment/main.tscn")
    print("3. File → Run Script → scripts/apply_poster_materials.gd")
    print("4. Save and run!")


if __name__ == "__main__":
    update_main_scene()
