@tool
extends EditorScript
## Helper script to automatically apply poster textures and update titles
## Run this from: File → Run Script (Ctrl+Shift+X)

func _run() -> void:
	print("Applying poster materials and updating titles...")

	var root = get_scene()
	if not root:
		print("Error: No scene open")
		return

	# Load poster data from backend
	var poster_data = _load_poster_data()
	if poster_data.is_empty():
		print("Warning: No poster data loaded, will only apply textures")

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

			# Get texture dimensions
			var tex_size = texture.get_size()
			var aspect_ratio = tex_size.x / tex_size.y

			# Adjust mesh size to match image aspect ratio
			# Keep height at 2.0, adjust width
			var mesh_height = 2.0
			var mesh_width = mesh_height * aspect_ratio
			if poster_mesh.mesh is BoxMesh:
				poster_mesh.mesh.size = Vector3(mesh_width, mesh_height, 0.05)

			# Create or update material
			var material = StandardMaterial3D.new()
			material.albedo_texture = texture
			material.albedo_color = Color.WHITE
			material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED  # Flat, unlit
			material.cull_mode = BaseMaterial3D.CULL_DISABLED  # Visible from both sides
			material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS

			# Apply material
			poster_mesh.set_surface_override_material(0, material)

			# Update title from poster data
			if poster_data.has(poster_id):
				var label = child.find_child("Label3D", false, false)
				if label:
					label.text = poster_data[poster_id]["title"]
					print("✓ Applied " + texture_path + " to " + child.name)
					print("  Title: " + poster_data[poster_id]["title"])
				else:
					print("✓ Applied " + texture_path + " to " + child.name + " (no label found)")
			else:
				print("✓ Applied " + texture_path + " to " + child.name + " (no data found)")

			booth_count += 1

	print("\n✓ Processed " + str(booth_count) + " poster booths")
	print("Save the scene to keep changes!")


func _load_poster_data() -> Dictionary:
	"""Load poster data from the backend posters.json file."""
	var data_path = "res://../backend/data/posters.json"
	var file = FileAccess.open(data_path, FileAccess.READ)

	if not file:
		print("Warning: Could not open " + data_path)
		return {}

	var json_text = file.get_as_text()
	file.close()

	var json = JSON.new()
	var error = json.parse(json_text)

	if error != OK:
		print("Warning: Could not parse posters.json")
		return {}

	var posters_array = json.get_data()
	if not posters_array is Array:
		print("Warning: posters.json is not an array")
		return {}

	# Convert array to dictionary keyed by poster_id
	var result = {}
	for poster in posters_array:
		if poster.has("id"):
			result[poster["id"]] = poster

	print("Loaded " + str(result.size()) + " posters from backend data")
	return result
