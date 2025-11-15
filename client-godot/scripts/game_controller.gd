extends Node
## Main game controller that coordinates player, UI, and agent interactions

@export var player_path: NodePath
@export var dialogue_ui_path: NodePath
@export var agent_service_path: NodePath
@export var interaction_prompt_path: NodePath

@onready var player = get_node(player_path) if player_path else null
@onready var dialogue_ui = get_node(dialogue_ui_path) if dialogue_ui_path else null
@onready var agent_service = get_node(agent_service_path) if agent_service_path else null
@onready var interaction_prompt = get_node(interaction_prompt_path) if interaction_prompt_path else null


func _ready() -> void:
	# Connect player interaction signal
	if player:
		player.interaction_requested.connect(_on_player_interaction_requested)

	# Connect dialogue UI to agent service
	if dialogue_ui and agent_service:
		dialogue_ui.agent_service_path = agent_service.get_path()

	# Check backend connection on startup
	if agent_service:
		agent_service.check_health()
		agent_service.response_received.connect(_on_health_check_response)

	print("MAD Game Controller initialized")


func _on_player_interaction_requested(target) -> void:
	if not target or not dialogue_ui:
		return

	# Get agent info from the interactable
	if target.has_method("get_agent_info"):
		var agent_info = target.get_agent_info()

		# Open dialogue UI
		dialogue_ui.open_dialogue(
			agent_info["agent_type"],
			agent_info["agent_name"],
			agent_info.get("poster_id", "")
		)

		# Call interact on the target
		if target.has_method("interact"):
			target.interact()


func _on_health_check_response(response_data: Dictionary) -> void:
	if response_data.has("status"):
		print("Backend status: ", response_data["status"])
		print("Posters loaded: ", response_data.get("posters_loaded", 0))
		print("Agents initialized: ", response_data.get("agents_initialized", 0))
