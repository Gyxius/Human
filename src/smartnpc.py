from characters import *
from weapons import *
from reward import *

class SmartNPC(Characters):
	def __init__(self, surface, clan, radius=RADIUS_SIZE, speed=1, vision=200, damage=10):
		self.xPosition = 0
		self.yPosition = 0
		self.radius = radius
		self.clan = clan
		if self.clan == "RED":
			self.color = RED
		elif self.clan == "BLUE":
			self.color = BLUE
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
		self.attack_reward = 0
		self.rewards = Reward()
		self.actions = ['MOVE_UP', 'MOVE_DOWN', 'MOVE_LEFT', 'MOVE_RIGHT', 'ATTACK_PLAYER', 'IDLE']
		self.total_reward = 0
		self.q_table = {}  # Q-values for state-action pairs
		self.epsilon = 0.1  # Exploration rate
		self.alpha = 0.1    # Learning rate
		self.gamma = 0.9    # Discount factor

	def get_state(self, npc_list):
		nearest_enemy = self.get_nearest_enemy(npc_list)
		if nearest_enemy:
			state = (
				self.xPosition,
				self.yPosition,
				self.health,
				nearest_enemy.xPosition,
				nearest_enemy.yPosition,
				nearest_enemy.health
			)
		else:
			state = (self.xPosition, self.yPosition, self.health, 0, 0, 0)
		return state

	def get_nearest_enemy(self, npc_list):
		enemies = [npc for npc in npc_list if npc.clan != self.clan and npc.alive]
		if not enemies:
			return None
		enemies.sort(key=lambda npc: ((npc.xPosition - self.xPosition) ** 2 + (npc.yPosition - self.yPosition) ** 2) ** 0.5)
		return enemies[0]

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
			# font = pygame.font.Font('freesansbold.ttf', 20)
			# text = font.render(str(int(self.total_reward)), True, BLACK, WHITE)
			# textRect = text.get_rect()
			# textRect.center = (self.xPosition, self.yPosition)
			# surface.blit(text, textRect)

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
		print(f"NPC {self.id} took {damage} damage! Health: {self.health}")
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
			print(f"NPC {self.id} target died during attack. Switching to IdleState.")
			self.target = []
			self.set_state(IdleState(self))
			return
		if not self.weapon.active and self.is_in_state(CloseState):
			print("attack enemy")
			self.weapon.attack(self)
			target = self.target[0]
			target.take_damage(self.weapon.damage, collision_manager.npcs, self)
			self.rewards.reward(10 + 0.5 * (100 - self.health), "attacked target")

	def act(self, action, collision_manager, npcs):
		reward = 0
		done = False

		low_health = self.health <= 20
		very_low_health = self.health <= 10

		if action == 'MOVE_UP':
			self.yPosition -= self.speed
			reward = -2 if not low_health else -1  # Less penalty when low health (escaping)
		elif action == 'MOVE_DOWN':
			self.yPosition += self.speed
			reward = -2 if not low_health else -1
		elif action == 'MOVE_LEFT':
			self.xPosition -= self.speed
			reward = -2 if not low_health else -1
		elif action == 'MOVE_RIGHT':
			self.xPosition += self.speed
			reward = -2 if not low_health else -1
		elif action == 'ATTACK_PLAYER':
			nearest_enemy = self.get_nearest_enemy(npcs)
			if nearest_enemy and self._target_is_close(nearest_enemy):
				self.target = [nearest_enemy]
				self.attack_target(collision_manager)
				nearest_enemy.take_damage(self.weapon.damage, collision_manager.npcs, self)
				if low_health:
					reward = -100  # Punish attacking while weak
				else:
					reward = 200  # Reward if healthy
			else:
				reward = -5
		elif action == 'IDLE':
			self.health = min(100, self.health + 1)  # Recover health
			reward = 5 if low_health else -1  # Reward resting when low health

		# Clamp position to stay in screen
		self.xPosition = max(RADIUS_SIZE, min(WIDTH - RADIUS_SIZE, self.xPosition))
		self.yPosition = max(RADIUS_SIZE, min(HEIGHT - RADIUS_SIZE, self.yPosition))

		# Add fear-based penalty for being very low health
		if very_low_health:
			reward -= 10  # Fear of imminent death

		self.total_reward += reward

		if not self.alive:
			done = True

		return reward, done

	def _target_is_close(self, player):
		dx = player.xPosition - self.xPosition
		dy = player.yPosition - self.yPosition
		distance = (dx ** 2 + dy ** 2) ** 0.5
		return distance <= 2.2 * RADIUS_SIZE

	def is_in_state(self, state_class):
		return isinstance(self.state, state_class)

	def reset(self, collision_manager):
		self.spawn(collision_manager)
		self.health = 100
		self.alive = True
		self.total_reward = 0
		self.target = []
		return self.get_state(collision_manager.npcs)

	def choose_action(self, state):
		if random.uniform(0, 1) < self.epsilon:
			return random.choice(self.actions)
		else:
			if state not in self.q_table:
				self.q_table[state] = [0] * len(self.actions)
			return self.actions[self.q_table[state].index(max(self.q_table[state]))]

	def update_q_table(self, state, action, reward, next_state):
		if state not in self.q_table:
			self.q_table[state] = [0] * len(self.actions)
		if next_state not in self.q_table:
			self.q_table[next_state] = [0] * len(self.actions)

		action_index = self.actions.index(action)
		best_next_q = max(self.q_table[next_state])
		self.q_table[state][action_index] += self.alpha * (
			reward + self.gamma * best_next_q - self.q_table[state][action_index]
		)