# NPC Character System for MAD

This document explains how to use the NPC character system to add humanoid figures near poster booths.

## What's Included

### Files Created

1. **`scripts/npc_character.gd`** - NPC behavior script
   - Idle bobbing animation
   - Gentle swaying
   - Head tracking (looks at player when nearby)

2. **`scenes/interactables/npc_character.tscn`** - Simple humanoid character
   - Built with basic Godot primitives (capsules, spheres)
   - Customizable colors and proportions
   - Includes nameplate label

3. **`scenes/interactables/poster_booth_with_npc.tscn`** - Poster booth with NPC
   - Extends the original poster booth
   - Includes NPC positioned beside the poster

## Quick Start

### Option 1: Use in New Scenes

When creating new poster booths, use `poster_booth_with_npc.tscn` instead of `poster_booth.tscn`.

### Option 2: Add to Existing Booths

In your main scene (e.g., `main.tscn`):

1. Open the scene in Godot
2. Find an existing PosterBooth node
3. Right-click → Add Child Node → "Instantiate Child Scene"
4. Select `scenes/interactables/npc_character.tscn`
5. Position the NPC:
   - Set Transform position to: `(1.2, 0, 0.5)` for right side
   - Or `(-1.2, 0, 0.5)` for left side
   - Rotate Y: `45°` to face toward the poster

### Option 3: Update All Booths with Script

You can run this GDScript from Godot's Script Editor to add NPCs to all existing booths:

```gdscript
# Run this from the Scene tab: File → Run Script
@tool
extends EditorScript

func _run():
	var npc_scene = load("res://scenes/interactables/npc_character.tscn")
	var main_scene = get_scene()

	# Find all PosterBooth nodes
	var booths = _find_nodes_by_type(main_scene, "PosterBooth")

	for booth in booths:
		# Check if NPC already exists
		if booth.has_node("NPC"):
			print("Booth already has NPC: ", booth.name)
			continue

		# Instance NPC
		var npc = npc_scene.instantiate()
		npc.name = "NPC"

		# Position beside the booth
		npc.transform.origin = Vector3(1.2, 0, 0.5)
		npc.rotation_degrees.y = -45

		booth.add_child(npc)
		npc.set_owner(main_scene)

		print("Added NPC to: ", booth.name)

	print("Finished adding NPCs!")

func _find_nodes_by_type(node: Node, type_name: String) -> Array:
	var result = []
	if node.name.begins_with(type_name):
		result.append(node)
	for child in node.get_children():
		result.append_array(_find_nodes_by_type(child, type_name))
	return result
```

## Customization

### Change NPC Appearance

Edit `scenes/interactables/npc_character.tscn`:

1. **Colors:**
   - Select `Body/Torso` → Material → Albedo Color (clothes color)
   - Select `Body/Head/HeadMesh` → Material → Albedo Color (skin tone)

2. **Proportions:**
   - Select `Body/Torso` → Mesh → Size
   - Select `Body/Head/HeadMesh` → Mesh → Radius

3. **Name Label:**
   - Select `NameLabel` → Text property

### Adjust Animation Parameters

Select the root NPCCharacter node and modify in Inspector:

- **Bob Speed** (default: 1.2) - How fast the character bobs up/down
- **Bob Height** (default: 0.03) - How much vertical movement
- **Sway Speed** (default: 0.8) - How fast the character sways
- **Sway Angle** (default: 3.0) - How much the character rotates
- **Look At Player** (default: true) - Whether head follows player
- **Look Speed** (default: 2.0) - How fast head tracking is

### Create Different NPC Variants

1. Duplicate `npc_character.tscn` → Save as `npc_character_variant1.tscn`
2. Change colors, sizes, or add accessories
3. Use different variants at different booths

Example variants:
- **Professor**: Larger head, darker clothes
- **Student**: Smaller size, brighter colors
- **Researcher**: Add glasses (CSGSphere3D in front of eyes)

## Upgrading to Better Models

The current NPCs use simple geometric shapes. For better quality:

### Free Model Sources

1. **Mixamo** (https://www.mixamo.com/)
   - Free rigged humanoid characters
   - Includes animations
   - Download as `.fbx`, convert to `.glb` in Blender

2. **Kenney Assets** (https://kenney.nl/assets/animated-characters)
   - Low-poly stylized characters
   - Already game-ready `.glb` files
   - MIT License (free for any use)

3. **Quaternius** (http://quaternius.com/)
   - Many free character packs
   - Various styles available
   - CC0 License (public domain)

### How to Import Better Models

1. Download a `.glb` or `.gltf` file
2. Copy to `client-godot/assets/characters/`
3. Godot will auto-import it
4. In Scene tab:
   - Expand the imported model
   - Right-click on the character node
   - "New Inherited Scene"
   - Save to `scenes/interactables/`
5. Attach the `npc_character.gd` script
6. Adjust the script to match the model's bone structure

### Example: Using Mixamo Character

1. Go to Mixamo, create account (free)
2. Select a character
3. Download with "T-Pose" animation, format: FBX
4. Open in Blender:
   - File → Import → FBX
   - File → Export → glTF 2.0 (.glb)
5. Copy `.glb` to `client-godot/assets/characters/`
6. In Godot, find the imported scene
7. Create inherited scene and attach `npc_character.gd`

## NPC Behavior Features

### Current Features

✅ **Idle Animation** - Gentle bobbing and swaying
✅ **Head Tracking** - Looks at player when within 3 meters
✅ **Name Label** - Displays character name above head
✅ **Smooth Transitions** - Lerped rotation for natural movement

### Future Enhancements (Not Yet Implemented)

Ideas for extending the NPC system:

- **Greeting Animation** - Wave when player first approaches
- **Facial Expressions** - Change expression during conversation
- **Voice Lines** - Play audio clips when interacted with
- **Randomized Idle** - Switch between multiple idle poses
- **Day/Night Variations** - Different behavior based on time
- **Path Following** - NPCs walk a patrol route
- **Gesture System** - Point at poster when explaining

## Troubleshooting

### NPC appears black/no material

- Check that materials are assigned in the scene
- Try re-saving the NPC scene
- Ensure StandardMaterial3D resources are not null

### NPC doesn't look at player

- Verify player is in "player" group (in Node tab)
- Check `look_at_player` is enabled in Inspector
- Ensure the NPC's Head node exists and is named correctly

### NPC animation is too fast/slow

- Adjust `bob_speed` and `sway_speed` in Inspector
- Values between 0.5-2.0 usually work well

### NPC blocks player movement

- NPCs are decorative and shouldn't have collision
- If needed, add a CharacterBody3D and configure collision layers
- Use collision_layer = 0 for decorative NPCs

## Examples

### Minimal NPC Setup

```gdscript
# Attach to any Node3D
extends Node3D

func _ready():
	var npc = load("res://scenes/interactables/npc_character.tscn").instantiate()
	npc.position = Vector3(0, 0, 2)
	add_child(npc)
```

### Multiple NPCs with Different Looks

```gdscript
# Create variety by randomizing colors
func create_npc_with_random_color() -> Node3D:
	var npc = load("res://scenes/interactables/npc_character.tscn").instantiate()

	# Find the torso mesh and randomize color
	var torso = npc.get_node("Body/Torso")
	if torso and torso is MeshInstance3D:
		var mat = torso.get_surface_override_material(0)
		if mat:
			mat = mat.duplicate()
			mat.albedo_color = Color(randf(), randf(), randf())
			torso.set_surface_override_material(0, mat)

	return npc
```

## Architecture

```
NPCCharacter (Node3D)
├─ npc_character.gd (Script)
├─ Body (Node3D) - Swaying root
│  ├─ Torso (MeshInstance3D)
│  ├─ Head (Node3D) - Rotation for looking
│  │  ├─ HeadMesh (MeshInstance3D)
│  │  └─ Eyes (Node3D)
│  │     ├─ LeftEye (CSGSphere3D)
│  │     │  └─ LeftPupil (CSGSphere3D)
│  │     └─ RightEye (CSGSphere3D)
│  │        └─ RightPupil (CSGSphere3D)
│  ├─ LeftArm (MeshInstance3D)
│  └─ RightArm (MeshInstance3D)
└─ NameLabel (Label3D)
```

## Credits

The NPC system was designed for the Multi-Agent Dungeon (MAD) project to provide visual representation of AI agents at research poster booths.

Feel free to modify and extend for your needs!
