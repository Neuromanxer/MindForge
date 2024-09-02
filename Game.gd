# Game.gd
extends Node
var Player1_MaxHP = 10
var Player2_MaxHP = 10
var Player3_MaxHP = 10
var Enemy1_MaxHP = 10
var Enemy2_MaxHP = 10
var Enemy3_MaxHP = 10
var Player1_HP = 10
var Player2_HP = 10
var Player3_HP = 10
var Enemy1_HP = 10
var Enemy2_HP = 10
var Enemy3_HP = 10

func update_health(character: Character) -> void:
	match character.identifier:
		"Player1":
			Player1_HP -= 1
		"Player2":
			Player2_HP -= 1
		"Player3":
			Player3_HP -= 1
		"Enemy1":
			Enemy1_HP -= 1
		"Enemy2":
			Enemy2_HP -= 1
		"Enemy3":
			Enemy3_HP -= 1
	print(character.identifier + " HP updated. Current HP: " + str(get_hp(character.identifier)))

func get_hp(title: String) -> int:
	match title:
		"Player1":
			return Player1_HP
		"Player2":
			return Player2_HP
		"Player3":
			return Player3_HP
		"Enemy1":
			return Enemy1_HP
		"Enemy2":
			return Enemy2_HP
		"Enemy3":
			return Enemy3_HP
		_:
			return 0
