extends Area3D
## Base class for interactable objects (poster booths, guide kiosk)

signal interacted(interactable)

@export_group("Interaction")
@export var interaction_prompt: String = "Press E to interact"
@export var agent_type: String = "guide"  # "guide" or "poster_host"
@export var agent_name: String = "Agent"
@export var poster_id: String = ""  # Only for poster_host

@export_group("Visual Feedback")
@export var highlight_on_hover: bool = true
@export var highlight_material: StandardMaterial3D

var player_in_range: bool = false
var original_materials: Dictionary = {}


func _ready() -> void:
	# Connect area signals
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

	# Set collision layer for interactables
	collision_layer = 2  # Layer 2: Interactable
	collision_mask = 4   # Detect Layer 3: Player


func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("player"):
		player_in_range = true
		_show_prompt()

		if highlight_on_hover:
			_apply_highlight()

		# Notify player that an interactable is available
		if body.has_method("set_interaction_target"):
			body.set_interaction_target(self)


func _on_body_exited(body: Node3D) -> void:
	if body.is_in_group("player"):
		player_in_range = false
		_hide_prompt()

		if highlight_on_hover:
			_remove_highlight()

		# Clear interaction target
		if body.has_method("clear_interaction_target"):
			body.clear_interaction_target()


func interact() -> void:
	"""Called when player presses interact key."""
	interacted.emit(self)


func get_agent_info() -> Dictionary:
	"""Return information needed to start a conversation."""
	return {
		"agent_type": agent_type,
		"agent_name": agent_name,
		"poster_id": poster_id
	}


func _show_prompt() -> void:
	# TODO: Show interaction prompt UI
	# For now, this will be implemented in the main scene
	pass


func _hide_prompt() -> void:
	# TODO: Hide interaction prompt UI
	pass


func _apply_highlight() -> void:
	if not highlight_material:
		return

	# Store original materials and apply highlight
	var mesh_instance = _find_mesh_instance(self)
	if mesh_instance:
		for i in mesh_instance.get_surface_override_material_count():
			if not original_materials.has(i):
				original_materials[i] = mesh_instance.get_surface_override_material(i)

		for i in mesh_instance.mesh.get_surface_count():
			mesh_instance.set_surface_override_material(i, highlight_material)


func _remove_highlight() -> void:
	var mesh_instance = _find_mesh_instance(self)
	if mesh_instance:
		for i in original_materials.keys():
			mesh_instance.set_surface_override_material(i, original_materials[i])
		original_materials.clear()


func _find_mesh_instance(node: Node) -> MeshInstance3D:
	"""Recursively find the first MeshInstance3D child."""
	if node is MeshInstance3D:
		return node

	for child in node.get_children():
		var result = _find_mesh_instance(child)
		if result:
			return result

	return null
