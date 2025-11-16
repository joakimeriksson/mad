extends Node3D
## NPC Character for poster booths
## Provides simple idle animation and looks at player when nearby

@export var bob_speed: float = 1.0
@export var bob_height: float = 0.05
@export var sway_speed: float = 0.8
@export var sway_angle: float = 5.0
@export var look_at_player: bool = true
@export var look_speed: float = 2.0

@onready var body: Node3D = $Body if has_node("Body") else null
@onready var head: Node3D = $Body/Head if has_node("Body/Head") else null

var time_passed: float = 0.0
var initial_position: Vector3
var initial_rotation: Vector3
var player: Node3D = null
var looking_at_player: bool = false


func _ready() -> void:
	initial_position = position
	if body:
		initial_rotation = body.rotation_degrees

	# Find player in scene
	await get_tree().process_frame
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		player = players[0]


func _process(delta: float) -> void:
	time_passed += delta

	# Idle animations
	_animate_idle()

	# Look at player if nearby
	if look_at_player and player and head:
		_look_at_player(delta)


func _animate_idle() -> void:
	"""Simple bobbing and swaying animation."""
	if not body:
		return

	# Vertical bobbing
	var bob_offset = sin(time_passed * bob_speed) * bob_height
	position.y = initial_position.y + bob_offset

	# Gentle swaying
	var sway = sin(time_passed * sway_speed) * sway_angle
	body.rotation_degrees.y = initial_rotation.y + sway


func _look_at_player(delta: float) -> void:
	"""Make the NPC head look at the player when nearby."""
	if not player:
		return

	var distance = global_position.distance_to(player.global_position)

	# Only look at player if within 3 meters
	if distance < 3.0:
		looking_at_player = true

		# Calculate direction to player
		var target_position = player.global_position
		# Adjust for player head height (approximate)
		target_position.y += 1.6

		# Smoothly rotate head towards player
		var direction = (target_position - head.global_position).normalized()
		var target_rotation = Vector3.ZERO

		# Calculate Y rotation (left-right)
		target_rotation.y = atan2(direction.x, direction.z)

		# Calculate X rotation (up-down) - limited range
		var horizontal_distance = Vector2(direction.x, direction.z).length()
		target_rotation.x = -atan2(direction.y, horizontal_distance)
		# Clamp to reasonable neck rotation
		target_rotation.x = clamp(target_rotation.x, deg_to_rad(-30), deg_to_rad(30))

		# Smoothly interpolate
		head.rotation.y = lerp_angle(head.rotation.y, target_rotation.y, look_speed * delta)
		head.rotation.x = lerp_angle(head.rotation.x, target_rotation.x, look_speed * delta)
	else:
		# Return to neutral position
		if looking_at_player:
			looking_at_player = false
			head.rotation = lerp(head.rotation, Vector3.ZERO, look_speed * delta)


func set_npc_name(npc_name: String) -> void:
	"""Set the NPC's display name."""
	# This could be used to show a nameplate above the NPC
	pass


func play_greeting() -> void:
	"""Play a greeting animation (can be expanded)."""
	# Could add a wave animation here
	pass
