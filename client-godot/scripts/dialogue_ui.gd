extends CanvasLayer
## Dialogue UI for interacting with agents

signal message_sent(message: String)
signal dialogue_closed

@export var agent_service_path: NodePath
@onready var agent_service = get_node(agent_service_path) if agent_service_path else null

# UI Elements (will be set in scene)
@onready var panel: Panel = $Panel
@onready var chat_history: RichTextLabel = $Panel/MarginContainer/VBoxContainer/ChatHistory
@onready var input_field: LineEdit = $Panel/MarginContainer/VBoxContainer/InputContainer/MessageInput
@onready var send_button: Button = $Panel/MarginContainer/VBoxContainer/InputContainer/SendButton
@onready var close_button: Button = $Panel/MarginContainer/VBoxContainer/TopBar/CloseButton
@onready var agent_label: Label = $Panel/MarginContainer/VBoxContainer/TopBar/AgentLabel

# Current conversation state
var current_agent_type: String = ""
var current_poster_id: String = ""
var current_agent_name: String = ""


func _ready() -> void:
	# Connect signals
	if send_button:
		send_button.pressed.connect(_on_send_button_pressed)
	if close_button:
		close_button.pressed.connect(_on_close_button_pressed)
	if input_field:
		input_field.text_submitted.connect(_on_message_submitted)

	# Connect to agent service
	if agent_service:
		agent_service.response_received.connect(_on_agent_response)
		agent_service.error_occurred.connect(_on_agent_error)

	# Start hidden
	hide()


func open_dialogue(agent_type: String, agent_name: String, poster_id: String = "") -> void:
	"""Open dialogue with a specific agent."""
	current_agent_type = agent_type
	current_poster_id = poster_id
	current_agent_name = agent_name

	# Update UI
	if agent_label:
		agent_label.text = "Chat with: " + agent_name

	# Clear chat history
	if chat_history:
		chat_history.clear()
		_add_system_message("Conversation started with " + agent_name)

	# Show UI and capture input
	show()
	if input_field:
		input_field.grab_focus()

	# Release mouse for UI interaction
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)


func close_dialogue() -> void:
	"""Close the dialogue UI."""
	hide()
	current_agent_type = ""
	current_poster_id = ""
	current_agent_name = ""

	# Recapture mouse for gameplay
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	dialogue_closed.emit()


func _on_send_button_pressed() -> void:
	_send_message()


func _on_message_submitted(_text: String) -> void:
	_send_message()


func _send_message() -> void:
	if not input_field or input_field.text.strip_edges() == "":
		return

	var message = input_field.text.strip_edges()
	input_field.text = ""

	# Display user message
	_add_user_message(message)

	# Send to backend
	if agent_service:
		agent_service.send_message_to_agent(current_agent_type, message, current_poster_id)
	else:
		_add_system_message("Error: Agent service not connected")

	message_sent.emit(message)


func _on_agent_response(response_data: Dictionary) -> void:
	if response_data.has("reply"):
		_add_agent_message(response_data["reply"])
	else:
		_add_system_message("Received invalid response")


func _on_agent_error(error_message: String) -> void:
	_add_system_message("Error: " + error_message)


func _add_user_message(message: String) -> void:
	if chat_history:
		chat_history.append_text("[color=lightblue][b]You:[/b][/color] " + message + "\n\n")


func _add_agent_message(message: String) -> void:
	if chat_history:
		chat_history.append_text("[color=lightgreen][b]" + current_agent_name + ":[/b][/color] " + message + "\n\n")


func _add_system_message(message: String) -> void:
	if chat_history:
		chat_history.append_text("[color=gray][i]" + message + "[/i][/color]\n\n")


func _on_close_button_pressed() -> void:
	close_dialogue()


func _input(event: InputEvent) -> void:
	# Close dialogue with ESC
	if event.is_action_pressed("ui_cancel") and visible:
		close_dialogue()
		get_viewport().set_input_as_handled()
