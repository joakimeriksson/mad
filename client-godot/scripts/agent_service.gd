extends Node
## Service for communicating with the MAD backend API

signal response_received(response_data: Dictionary)
signal error_occurred(error_message: String)

# API Configuration
@export var api_url: String = "http://localhost:8000"

var http_request: HTTPRequest


func _ready() -> void:
	# Create HTTP request node
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)


func send_message_to_agent(agent_type: String, message: String, poster_id: String = "") -> void:
	"""
	Send a message to an agent (guide or poster_host).

	Args:
		agent_type: "guide" or "poster_host"
		message: The user's message
		poster_id: Required for poster_host agents
	"""
	var request_body = {
		"agent_type": agent_type,
		"message": message
	}

	if poster_id != "":
		request_body["poster_id"] = poster_id

	var json = JSON.stringify(request_body)
	var headers = ["Content-Type: application/json"]

	var error = http_request.request(
		api_url + "/agent",
		headers,
		HTTPClient.METHOD_POST,
		json
	)

	if error != OK:
		error_occurred.emit("Failed to send request: " + str(error))


func get_posters() -> void:
	"""Fetch all available posters from the API."""
	var error = http_request.request(api_url + "/posters")

	if error != OK:
		error_occurred.emit("Failed to fetch posters: " + str(error))


func get_poster(poster_id: String) -> void:
	"""Fetch details for a specific poster."""
	var error = http_request.request(api_url + "/posters/" + poster_id)

	if error != OK:
		error_occurred.emit("Failed to fetch poster: " + str(error))


func check_health() -> void:
	"""Check API health status."""
	var error = http_request.request(api_url + "/health")

	if error != OK:
		error_occurred.emit("Failed to check health: " + str(error))


func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS:
		error_occurred.emit("HTTP Request failed with result: " + str(result))
		return

	if response_code != 200:
		error_occurred.emit("HTTP Response code: " + str(response_code))
		return

	var json = JSON.new()
	var parse_result = json.parse(body.get_string_from_utf8())

	if parse_result != OK:
		error_occurred.emit("Failed to parse JSON response")
		return

	var response_data = json.get_data()
	response_received.emit(response_data)
