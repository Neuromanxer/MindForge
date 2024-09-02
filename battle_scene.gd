extends Node2D

@export var player_group: Node2D
@export var enemy_group: Node2D
@export var timeline: HBoxContainer
@onready var choice: VBoxContainer = $CanvasLayer/choice
@onready var enemy_party: Node2D = $enemy_party

var index: int = 0
var sorted_array = []
var players: Array[Character] = []
var enemies: Array[Character] = []
var action_queue: Array = []
var node
var is_battling = false
@export var options: VBoxContainer
@export var enemy_button: PackedScene

func _ready():
	for player in player_group.get_children():
		players.append(player.character)

	for enemy in enemy_group.get_children():
		enemies.append(enemy.character)

		var button = enemy_button.instantiate()
		button.character = enemy.character
		$CanvasLayer/EnemySelection.add_child(button)
		# Set a unique identifier for each button
		button.name = "EnemyButton_" + str(enemies.size())
		button.set_meta("enemy_index", enemies.size() - 1)  # Store enemy index in metadata
		button.connect("pressed", Callable(self, "_on_enemy_button_pressed").bind(enemies.size()))
		print(button.name)
	sort_and_display()
	EventBus.next_attack.connect(next_attack)
	next_attack()

func sort_combined_queue():
	var player_array = []
	for player in players:
		for i in player.queue:
			player_array.append({"character": player, "time": i})
	var enemy_array = []
	for enemy in enemies:
		for i in enemy.queue:
			enemy_array.append({"character": enemy, "time": i})
	sorted_array = player_array
	sorted_array.append_array(enemy_array)
	sorted_array.sort_custom(sort_by_time)

func _on_enemy_button_pressed(enemy_index: int) -> void:
	# Call the decrease_enemy_hp function with the appropriate enemy index
	decrease_enemy_hp(enemy_index)

func sort_by_time(a, b):
	return a["time"] < b["time"]

func update_timeline():
	var index: int = 0
	for slot in timeline.get_children():
		slot.find_child("TextureRect").texture = sorted_array[index]["character"].icon
		index += 1

func sort_and_display():
	sort_combined_queue()
	update_timeline()
	if sorted_array[0]['character'] in players:
		show_options()

func pop_out():
	sorted_array[0]["character"].pop_out()
	sort_and_display()
	
func attack():
	var attacking_character = sorted_array[0]["character"]

	# Ensure attack animation is only played once
	if attacking_character.node and attacking_character.node.has_method("attack"):
		attacking_character.node.attack()

	attacking_character.attack(get_tree())

	# Check if the attacking character is an enemy
	if attacking_character.title in ["Enemy1", "Enemy2", "Enemy3"]:
		# Ensure enemy attack animation and damage are processed once
		if attacking_character.node.has_method("play_attack_animation"):
			attacking_character.node.play_attack_animation()

		# Enemy attacks a random player
		decrease_player_hp()  # Enemy attacks a random player

	# Check if the attacking character is a player and should attack an enemy
	else:
		# If the character is a player, process the attack on the enemy
		choose_enemy()  # Allow player to choose which enemy to attack


func decrease_player_hp() -> void:
	# Generate a random integer between 1 and 3
	var random_player = randi_range(1, 3)  # Use randi_range for integer selection

	match random_player:
		1:
			if Game.Player1_HP > 0:
				Game.Player1_HP = max(0, Game.Player1_HP - 1)
				if player_group.get_child(0).has_method("take_damage"):
					player_group.get_child(0).take_damage(1)
		2:
			if Game.Player2_HP > 0:
				Game.Player2_HP = max(0, Game.Player2_HP - 1)
				if player_group.get_child(1).has_method("take_damage"):
					player_group.get_child(1).take_damage(1)
		3:
			if Game.Player3_HP > 0:
				Game.Player3_HP = max(0, Game.Player3_HP - 1)
				if player_group.get_child(2).has_method("take_damage"):
					player_group.get_child(2).take_damage(1)

func decrease_enemy_hp(enemy: int) -> void:
	match enemy:
		1:
			if Game.Enemy1_HP > 0:  # Ensure only one damage is processed
				Game.Enemy1_HP = max(0, Game.Enemy1_HP - 1)
				if enemy_group.get_child(0).has_method("take_damage"):
					enemy_group.get_child(0).take_damage(1)
		2:
			if Game.Enemy2_HP > 0:  # Ensure only one damage is processed
				Game.Enemy2_HP = max(0, Game.Enemy2_HP - 1)
				if enemy_group.get_child(1).has_method("take_damage"):
					enemy_group.get_child(1).take_damage(1)
		3:
			if Game.Enemy3_HP > 0:  # Ensure only one damage is processed
				Game.Enemy3_HP = max(0, Game.Enemy3_HP - 1)
				if enemy_group.get_child(2).has_method("take_damage"):
					enemy_group.get_child(2).take_damage(1)

func next_attack():
	if sorted_array[0]['character'] in players:
		return
	attack()
	pop_out()

func show_options():
	options.show()
	options.get_child(0).grab_focus()

func choose_enemy():
	$CanvasLayer/EnemySelection.show()
	$CanvasLayer/EnemySelection.get_child(0).grab_focus()
