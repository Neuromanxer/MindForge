extends Node2D
#
@onready var choice: VBoxContainer = $"../CanvasLayer/choice"

var players: Array = []
var index : int = 0

func _ready():
	players = get_children()


func _on_enemy_party_next_player() -> void:
	if index <players.size() -1:
		index += 1
		switch_focus(index, index-1)
	else:
		index = 0
		switch_focus(index, players.size()-1)

func switch_focus(x, y):
	players[x].focus()
	players[y].unfocus()
