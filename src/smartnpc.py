from characters import *
from weapons import *
from reward import *

class SmartNPC(Characters):
	def __init__(self, surface, clan, radius=RADIUS_SIZE, speed=2, vision=200, damage=10):
		self.xPosition = 0
		self.yPosition = 0
		self.radius = radius
		self.clan = clan
		if self.clan == "RED":
			self.color = RED
			# self.xPosition = 20
			# self.yPosition = 20
		elif self.clan == "BLUE":
			self.color = BLUE
			# self.xPosition = 50
			# self.yPosition = 50
		sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition, self.radius)
		super().__init__(sprite, "npc")
		self.state = IdleState(self)
		self.speed = speed
		self.damage = damage
		self.vision = vision
		self.dx = 0
		self.dy = 0
		self.attack_speed = 5
		self.weapon = NoWeapon(self)
		self.player = False
		self.target = []
		self.wood = 0
		self.attack_reward = 0  # TODO BUILD THE REWARD SYSTEM USING THE CLASS
		self.rewards = Reward()
		self.actions = ['MOVE_LEFT', 'MOVE_UP', 'MOVE_DOWN', 'MOVE_RIGHT', 'ATTACK_PLAYER', 'IDLE']
		self.total_reward = 0
		self.q_table = {}  # Q-values for state-action pairs
		self.epsilon = 0.3  # Exploration rate
		self.alpha = 0.1    # Learning rate
		self.gamma = 0.9    # Discount factor

	def get_state(self, npc_list):
		def bucketize(value, bucket_size):
			return int(value // bucket_size)
		MAX_DISTANCE = (WIDTH ** 2 + HEIGHT ** 2) ** 0.5  # Screen diagonal distance
		nearest_enemy = self.get_nearest_npcs(npc_list)
		nearest_ally = self.get_nearest_npcs(npc_list, ally=True)

		ally_dx, ally_dy, ally_health, ally_distance = 0, 0, 0, 0
		enemy_dx, enemy_dy, enemy_health, enemy_distance = 0, 0, 0, 0

		if nearest_ally:
			ally_dx = nearest_ally.xPosition - self.xPosition
			ally_dy = nearest_ally.yPosition - self.yPosition
			ally_health = nearest_ally.health
			ally_distance = ((ally_dx ** 2 + ally_dy ** 2) ** 0.5)

		if nearest_enemy:
			enemy_dx = nearest_enemy.xPosition - self.xPosition
			enemy_dy = nearest_enemy.yPosition - self.yPosition
			enemy_health = nearest_enemy.health
			enemy_distance = ((enemy_dx ** 2 + enemy_dy ** 2) ** 0.5)

		# Bucket sizes for dx/dy = 10, health = 10, distances normalized
		bucket_size = 10
		state = (
			bucketize(self.health, bucket_size),  # Self health bucket (0-10)
			bucketize(ally_dx, bucket_size), bucketize(ally_dy, bucket_size), bucketize(ally_health, bucket_size), bucketize(ally_distance / MAX_DISTANCE * 10, 1),
			bucketize(enemy_dx, bucket_size), bucketize(enemy_dy, bucket_size), bucketize(enemy_health, bucket_size), bucketize(enemy_distance / MAX_DISTANCE * 10, 1)
		)

		return state

	def get_nearest_npcs(self, npc_list, ally=False):
		if not ally:
			npcs = [npc for npc in npc_list if npc.clan != self.clan and npc.alive]
		else:
			npcs = [npc for npc in npc_list if npc.clan == self.clan and npc.alive]
		if not npcs:
			return None
		npcs.sort(key=lambda npc: ((npc.xPosition - self.xPosition) ** 2 + (npc.yPosition - self.yPosition) ** 2) ** 0.5)
		return npcs[0]

	def spawn(self, collision_manager):
		xPosition = random.randint(RADIUS_SIZE, WIDTH - RADIUS_SIZE)
		yPosition = random.randint(RADIUS_SIZE, HEIGHT - RADIUS_SIZE)
		while collision_manager.is_colliding_circle(self, xPosition, yPosition):
			xPosition = random.randint(RADIUS_SIZE, WIDTH - RADIUS_SIZE)
			yPosition = random.randint(RADIUS_SIZE, HEIGHT - RADIUS_SIZE)
		self.xPosition = xPosition
		self.yPosition = yPosition

	def draw(self, surface):
		if self.alive:
			self.sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition, self.radius)
			self.healthbar.draw(surface)
			font = pygame.font.Font('freesansbold.ttf', 15)
			text = font.render(str(int(self.total_reward)), True, BLACK, WHITE)
			textRect = text.get_rect()
			textRect.center = (self.xPosition, self.yPosition)
			surface.blit(text, textRect)

	def update(self, characters, collision_manager):
		pass

	def set_state(self, state):
		self.state = state

	@property
	def collision_block(self):
		return pygame.Rect(self.xPosition - RADIUS_SIZE, self.yPosition - RADIUS_SIZE, self.width, self.height)

	def take_damage(self, damage, npc_list, attacker):
		if attacker.clan == self.clan:
			return
		self.health -= damage
		if self.target and self.target[0]:
			self.target[0] = attacker
		# print(f"NPC {self.id} took {damage} damage! Health: {self.health}")
		self.rewards.reward(-5 - 0.5 * (100 - self.health), "Getting attacked")
		if self.health <= 0:
			self.alive = False
			print(f"NPC {self.id} has died!")
			if self in npc_list:
				npc_list.remove(self)
			for npc in npc_list:
				if npc.target and npc.target[0] == self:
					npc.target = []
					npc.set_state(IdleState(npc))

	def attack_target(self, collision_manager):
		if self.target and not self.target[0].alive:
			# print(f"NPC {self.id} target died during attack. Switching to IdleState.")
			self.target = []
			self.set_state(IdleState(self))
			return
		if not self.weapon.active and self.is_in_state(CloseState):
			# print("attack enemy")
			self.weapon.attack(self)
			target = self.target[0]
			target.take_damage(self.weapon.damage, collision_manager.npcs, self)
			self.rewards.reward(10 + 0.5 * (100 - self.health), "attacked target")

	def act(self, action, collision_manager, npcs):
		reward = 0
		done = False

		dx, dy = 0, 0
		if action == 'MOVE_UP':
			dy -= self.speed
		elif action == 'MOVE_DOWN':
			dy += self.speed
		elif action == 'MOVE_LEFT':
			dx -= self.speed
		elif action == 'MOVE_RIGHT':
			dx += self.speed

		# Collision Check!
		if action in ['MOVE_UP', 'MOVE_DOWN', 'MOVE_LEFT', 'MOVE_RIGHT']:
			self.xPosition += dx
			self.yPosition += dy
			if collision_manager.is_colliding_circle(self, dx, dy):
				# self.xPosition += dx
				# self.yPosition += dy
				# ❌ Can't move, hit something
				reward = -10  # Penalize for bad move
				# print(f"Collision detected at ({self.xPosition}, {self.yPosition}) trying to move {action}")
			else:
				# ✅ Move allowed
				# self.xPosition += dx
				# self.yPosition += dy
				reward = 0  # Normal move cost
				# print(f"Moved {action} to ({self.xPosition}, {self.yPosition})")

		

		elif action == 'ATTACK_PLAYER':
			# Same as before: attack logic
			nearest_enemy = self.get_nearest_npcs(npcs)
			if nearest_enemy and self._target_is_close(nearest_enemy) and not collision_manager.is_colliding_circle(self, dx, dy):
				self.target = [nearest_enemy]
				self.attack_target(collision_manager)
				nearest_enemy.take_damage(self.weapon.damage, collision_manager.npcs, self)
				reward = 200
			else:
				reward = -5

		elif action == 'IDLE':
			self.health = min(100, self.health + 1)
			reward = -10  # Bigger penalty for doing nothing

		# Keep NPC on screen
		self.xPosition = max(RADIUS_SIZE, min(WIDTH - RADIUS_SIZE, self.xPosition))
		self.yPosition = max(RADIUS_SIZE, min(HEIGHT - RADIUS_SIZE, self.yPosition))

		self.total_reward += reward

		if not self.alive:
			done = True

		return reward, done

	def _target_is_close(self, player):
		dx = player.xPosition - self.xPosition
		dy = player.yPosition - self.yPosition
		distance = (dx ** 2 + dy ** 2) ** 0.5
		return distance <= 3 * RADIUS_SIZE

	def is_in_state(self, state_class):
		return isinstance(self.state, state_class)

	def reset(self, collision_manager):
		self.spawn(collision_manager)
		self.health = 100
		self.alive = True
		self.total_reward = 0
		self.target = []
		return self.get_state(collision_manager.npcs)

	def choose_action(self, state, collision_manager):
		""" Returns the best action to take """
		if random.uniform(0, 1) < self.epsilon:
			action = random.choice(self.actions)
		else:
			if state not in self.q_table:
				self.q_table[state] = [0] * len(self.actions)
			action = self.actions[self.q_table[state].index(max(self.q_table[state]))]

		return action

	def update_q_table(self, state, action, reward, next_state, training_mode=False):
		if not training_mode:
			return  # Don't update during play

		if state not in self.q_table:
			self.q_table[state] = [0] * len(self.actions)
		if next_state not in self.q_table:
			self.q_table[next_state] = [0] * len(self.actions)

		action_index = self.actions.index(action)
		best_next_q = max(self.q_table[next_state])
		self.q_table[state][action_index] += self.alpha * (
			reward + self.gamma * best_next_q - self.q_table[state][action_index]
		)