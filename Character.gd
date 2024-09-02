extends Resource
class_name Character

@export var title: String
@export var icon : Texture2D
	
@export var agility: int:
	set(value):
		agility = value
		speed = int(200.0 / (log(agility) + 2) - 25)
		queue_reset()
var speed : float
var queue: Array[float]
var status = 1
var node
	
func queue_reset():
	queue.clear()
	for i in range(4):
		if queue.size() == 0:
			queue.append(speed * status)
		else:
			queue.append(queue[-1] + speed * status)
func tween_movement(shift, tree):
	var tween = tree.create_tween()
	tween.tween_property(node, "position", node.position + shift, 0.2)
	await tween.finished

func attack(tree):
	var shift = Vector2(30, 0)
	if node.position.x < node.get_viewport_rect().size.x/2:
		shift = -shift
	await tween_movement(-shift, tree)
	await tween_movement(shift, tree)
	
	EventBus.next_attack.emit()
	
func pop_out():
	queue.pop_front()
	queue.append(queue[-1] * speed * status)
func set_status(status_type : String):
	match status_type:
		"Haste":
			status = 0.5
		"Slow":
			status = 2
 
	print(queue)
	for i in range(3):
		queue.pop_back()
	print(queue)
 
	for i in range(3):
		queue.append(queue[-1] + speed * status)
	print(queue)
