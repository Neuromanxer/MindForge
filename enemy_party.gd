extends Node2D


var enemies: Array = []
var index: int = 0
var action_queue: Array = []
var is_battling = false
signal next_player



func _ready():
	enemies = get_children()


func _process(_delta):

	if Input.is_action_just_pressed("ui_up"):
		if index > 0:
			index -= 1
			switch_focus(index, index + 1)
	if Input.is_action_just_pressed("ui_down"):
		if index < enemies.size() - 1:
			index += 1
			switch_focus(index, index - 1)
	if Input.is_action_just_pressed("ui_accept"):
		action_queue.push_back(index)
		emit_signal("next_player")

	if action_queue.size() == enemies.size() and not is_battling:
		is_battling = true
		_action(action_queue)

func _action(stack):
	action_queue.clear()
	is_battling = false
func switch_focus(x: int, y: int) -> void:
	enemies[x].focus()
	enemies[y].unfocus()

func _reset_focus():
	index = 0
	for enemy in enemies:
		enemy.unfocus()
func _start_choosing():
	_reset_focus()
	enemies[0].focus()

func _on_attack_pressed() -> void:
	_start_choosing()
