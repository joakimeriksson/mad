extends CharacterBody3D
## First-person player controller with WASD movement and mouse look

# Movement settings
@export var walk_speed: float = 5.0
@export var sprint_speed: float = 8.0
@export var jump_velocity: float = 4.5
@export var mouse_sensitivity: float = 0.003

# Camera settings
@export var camera_path: NodePath
@onready var camera: Camera3D = get_node(camera_path) if camera_path else null

# Physics
var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

# Mouse look
var mouse_motion: Vector2 = Vector2.ZERO
var camera_rotation: Vector2 = Vector2.ZERO

# Interaction
signal interaction_requested(target)
var interaction_target = null


func _ready() -> void:
	# Capture mouse
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	# Find camera if not set
	if not camera:
		camera = $Camera3D if has_node("Camera3D") else null


func _input(event: InputEvent) -> void:
	# Mouse look
	if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		mouse_motion = event.relative

	# Release mouse with ESC
	if event.is_action_pressed("ui_cancel"):
		if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		else:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	# Interaction
	if event.is_action_pressed("interact"):
		if interaction_target:
			interaction_requested.emit(interaction_target)


func _physics_process(delta: float) -> void:
	# Apply mouse look
	if mouse_motion.length() > 0:
		_apply_mouse_look(delta)
		mouse_motion = Vector2.ZERO

	# Add gravity
	if not is_on_floor():
		velocity.y -= gravity * delta

	# Handle jump
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_velocity

	# Get input direction
	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_backward")

	# Calculate movement direction
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

	# Apply movement
	var current_speed = sprint_speed if Input.is_action_pressed("ui_shift") else walk_speed
	if direction:
		velocity.x = direction.x * current_speed
		velocity.z = direction.z * current_speed
	else:
		velocity.x = move_toward(velocity.x, 0, current_speed)
		velocity.z = move_toward(velocity.z, 0, current_speed)

	move_and_slide()


func _apply_mouse_look(delta: float) -> void:
	if not camera:
		return

	# Rotate player horizontally
	rotate_y(-mouse_motion.x * mouse_sensitivity)

	# Rotate camera vertically
	camera_rotation.x -= mouse_motion.y * mouse_sensitivity
	camera_rotation.x = clamp(camera_rotation.x, -PI/2, PI/2)
	camera.rotation.x = camera_rotation.x


func set_interaction_target(target) -> void:
	interaction_target = target


func clear_interaction_target() -> void:
	interaction_target = null
