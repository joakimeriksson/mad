@tool
extends EditorScript
## Helper script to automatically apply poster textures to all booths
## Run this from: File → Run Script (Ctrl+Shift+X)

func _run() -> void:
	print("Applying poster materials to all booths...")

	var root = get_scene()
	if not root:
		print("Error: No scene open")
		return

	# Find the Interactables node
	var interactables = root.find_child("Interactables", true, false)
	if not interactables:
		print("Error: Interactables node not found")
		return

	var booth_count = 0

	# Process all poster booths
	for child in interactables.get_children():
		if child.name.begins_with("PosterBooth"):
			var poster_id = child.poster_id
			if poster_id == "":
				print("Warning: " + child.name + " has no poster_id set")
				continue

			# Find the PosterMesh
			var poster_mesh = child.find_child("PosterMesh", false, false)
			if not poster_mesh:
				print("Warning: No PosterMesh found in " + child.name)
				continue

			# Load the texture
			var texture_path = "res://assets/posters/" + poster_id + ".png"
			var texture = load(texture_path)

			if not texture:
				print("Warning: Could not load texture: " + texture_path)
				continue

			# Create or update material
			var material = StandardMaterial3D.new()
			material.albedo_texture = texture
			material.albedo_color = Color.WHITE
			material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED  # Flat, unlit
			material.cull_mode = BaseMaterial3D.CULL_DISABLED  # Visible from both sides

			# Apply material
			poster_mesh.set_surface_override_material(0, material)

			print("✓ Applied " + texture_path + " to " + child.name)
			booth_count += 1

	print("\n✓ Applied materials to " + str(booth_count) + " poster booths")
	print("Save the scene to keep changes!")
