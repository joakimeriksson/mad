extends Node
## Service for voice input/output (TTS and STT)

signal speech_to_text_result(text: String)
signal speech_to_text_error(error: String)
signal tts_started
signal tts_finished

# TTS Configuration
@export var tts_enabled: bool = true
@export var use_backend_tts: bool = true  # Use backend Edge TTS (better quality) vs local TTS
@export var backend_url: String = "http://localhost:8000"
@export var tts_voice: String = "en-US-female"  # For backend TTS
@export var tts_volume: float = 50.0  # 0-100 (for local TTS only)
@export var tts_pitch: float = 1.0    # 0.5-2.0 (for local TTS only)
@export var tts_rate: float = 1.0     # 0.1-10.0 (for local TTS only)
@export var tts_interrupt: bool = true

# STT Configuration
@export var stt_enabled: bool = true
@export var whisper_api_url: String = "http://localhost:11434/api/generate"  # Ollama endpoint
@export var whisper_model: String = "whisper"  # Or use OpenAI API

var current_utterance_id: int = 0
# var audio_recorder  # TODO: Implement with AudioStreamMicrophone for STT
var recording: bool = false
var http_request_stt: HTTPRequest
var http_request_tts: HTTPRequest
var audio_player: AudioStreamPlayer
var current_audio_file: String = ""


func _ready() -> void:
	# Check TTS availability
	if use_backend_tts:
		print("Using backend Edge TTS for high-quality voices")
	elif tts_enabled and DisplayServer.tts_get_voices().size() > 0:
		print("Using local TTS with ", DisplayServer.tts_get_voices().size(), " voices")
	else:
		print("TTS not available on this platform")
		tts_enabled = false

	# Setup HTTP request for STT
	http_request_stt = HTTPRequest.new()
	add_child(http_request_stt)
	http_request_stt.request_completed.connect(_on_stt_request_completed)

	# Setup HTTP request for TTS (backend)
	http_request_tts = HTTPRequest.new()
	add_child(http_request_tts)
	http_request_tts.request_completed.connect(_on_tts_request_completed)

	# Setup audio player for backend TTS
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	audio_player.finished.connect(_on_audio_finished)


## Text-to-Speech Functions

func speak(text: String) -> void:
	"""Convert text to speech using either backend Edge TTS or local TTS."""
	if not tts_enabled:
		print("TTS is disabled")
		return

	if use_backend_tts:
		_speak_backend(text)
	else:
		_speak_local(text)


func _speak_backend(text: String) -> void:
	"""Use backend Edge TTS for high-quality voice."""
	# Stop any current playback
	if audio_player.playing:
		audio_player.stop()

	# Make request to backend TTS endpoint
	var url = backend_url + "/tts?text=" + text.uri_encode()
	if tts_voice != "":
		url += "&voice=" + tts_voice.uri_encode()

	var error = http_request_tts.request(url, [], HTTPClient.METHOD_POST)

	if error == OK:
		tts_started.emit()
		print("Requesting TTS from backend: ", text.substr(0, 50), "...")
	else:
		print("Failed to request TTS: ", error)


func _speak_local(text: String) -> void:
	"""Use Godot's built-in TTS (lower quality)."""
	# Stop any current speech if interrupt is enabled
	if tts_interrupt and DisplayServer.tts_is_speaking():
		DisplayServer.tts_stop()

	# Get available voices
	var voices = DisplayServer.tts_get_voices()
	if voices.is_empty():
		print("No TTS voices available")
		return

	# Use first available voice (or could select by language/gender)
	# voices[0] is a Dictionary with "id", "name", "language" fields
	var voice_id = voices[0]["id"] if voices[0].has("id") else ""
	if voice_id == "":
		print("Invalid voice ID")
		return

	# Generate unique utterance ID
	current_utterance_id += 1

	# Speak the text
	DisplayServer.tts_speak(
		text,
		voice_id,
		tts_volume,
		tts_pitch,
		tts_rate,
		current_utterance_id,
		tts_interrupt
	)

	tts_started.emit()
	print("Speaking: ", text.substr(0, 50), "...")


func stop_speaking() -> void:
	"""Stop current TTS playback."""
	if use_backend_tts:
		if audio_player and audio_player.playing:
			audio_player.stop()
			tts_finished.emit()
	elif tts_enabled:
		DisplayServer.tts_stop()
		tts_finished.emit()


func is_speaking() -> bool:
	"""Check if TTS is currently speaking."""
	if use_backend_tts:
		return audio_player and audio_player.playing
	else:
		return tts_enabled and DisplayServer.tts_is_speaking()


func get_available_voices() -> Array:
	"""Get list of available TTS voices."""
	if tts_enabled:
		return DisplayServer.tts_get_voices()
	return []


func get_voices_for_language(language: String) -> PackedStringArray:
	"""Get voices for a specific language (e.g., 'en', 'sv')."""
	if tts_enabled:
		return DisplayServer.tts_get_voices_for_language(language)
	return PackedStringArray()


## Speech-to-Text Functions

func start_recording() -> void:
	"""Start recording audio for speech-to-text.

	Note: This is a placeholder. Godot doesn't have built-in STT.
	For production, you would need to:
	1. Record audio using AudioStreamMicrophone
	2. Save to WAV file
	3. Send to Whisper API (local or OpenAI)
	4. Parse response
	"""
	if not stt_enabled:
		print("STT is disabled")
		return

	recording = true
	print("Recording started... (STT implementation needed)")
	# TODO: Implement actual audio recording
	# This requires AudioStreamMicrophone and file I/O


func stop_recording() -> void:
	"""Stop recording and process speech-to-text."""
	if not recording:
		return

	recording = false
	print("Recording stopped, processing...")

	# TODO: Send audio to Whisper API
	# For now, emit a test result
	await get_tree().create_timer(0.5).timeout
	speech_to_text_result.emit("[Voice input not yet implemented]")


func send_audio_to_whisper(audio_file_path: String) -> void:
	"""Send audio file to Whisper API for transcription.

	This is a placeholder for future implementation.
	You'll need to integrate with either:
	- Local Whisper via Ollama
	- OpenAI Whisper API
	- Other STT service
	"""
	# TODO: Implement Whisper API call
	var headers = ["Content-Type: application/json"]

	# This is a simplified example - actual implementation depends on API
	var request_body = {
		"model": whisper_model,
		"file": audio_file_path
	}

	# Make request (implementation needed)
	print("STT: Would send audio to: ", whisper_api_url)


func _on_tts_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	"""Handle TTS API response - play the received audio file."""
	if result != HTTPRequest.RESULT_SUCCESS:
		print("TTS request failed: ", result)
		return

	if response_code != 200:
		print("TTS response code: ", response_code)
		return

	# Save audio to temporary file
	var temp_dir = OS.get_user_data_dir()
	current_audio_file = temp_dir + "/temp_tts.mp3"

	var file = FileAccess.open(current_audio_file, FileAccess.WRITE)
	if file:
		file.store_buffer(body)
		file.close()

		# Load and play audio
		var audio_stream = AudioStreamMP3.new()
		audio_stream.data = body

		audio_player.stream = audio_stream
		audio_player.play()
		print("Playing TTS audio...")
	else:
		print("Failed to save TTS audio file")


func _on_audio_finished() -> void:
	"""Called when TTS audio playback finishes."""
	tts_finished.emit()
	print("TTS audio finished")


func _on_stt_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	"""Handle STT API response."""
	if result != HTTPRequest.RESULT_SUCCESS:
		speech_to_text_error.emit("STT request failed: " + str(result))
		return

	if response_code != 200:
		speech_to_text_error.emit("STT response code: " + str(response_code))
		return

	# Parse response (format depends on API)
	var json = JSON.new()
	var parse_result = json.parse(body.get_string_from_utf8())

	if parse_result == OK:
		var response_data = json.get_data()
		if response_data.has("text"):
			speech_to_text_result.emit(response_data["text"])
		else:
			speech_to_text_error.emit("No text in STT response")
	else:
		speech_to_text_error.emit("Failed to parse STT response")


## Configuration

func set_tts_voice(voice_id: String) -> void:
	"""Set preferred TTS voice."""
	# Voice will be used in next speak() call
	pass


func set_tts_volume(volume: float) -> void:
	"""Set TTS volume (0-100)."""
	tts_volume = clamp(volume, 0.0, 100.0)


func set_tts_speed(rate: float) -> void:
	"""Set TTS speaking rate (0.1-10.0)."""
	tts_rate = clamp(rate, 0.1, 10.0)


func set_tts_pitch(pitch: float) -> void:
	"""Set TTS pitch (0.5-2.0)."""
	tts_pitch = clamp(pitch, 0.5, 2.0)
