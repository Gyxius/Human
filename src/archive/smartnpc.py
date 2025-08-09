from characters import *
from weapons import *
from reward import *

class SmartNPC(Characters):
	def __init__(self, surface, clan, q_table, radius=RADIUS_SIZE, speed=2, vision=200, damage=10):
		self.xPosition = 0
		self.yPosition = 0
		self.radius = radius
		self.clan = clan
		if self.clan == "RED":
			self.color = RED
			self.grid_character = 'R'
		elif self.clan == "BLUE":
			self.color = WHITE
			self.grid_character = 'B'
		sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition, self.radius)
		super().__init__(sprite, "npc")
		self.state = IdleState(self)
		self.speed = speed
		self.damage = damage
		self.movement_speed = 300
		self.vision = vision
		self.dx = 0
		self.dy = 0
		self.x = 0
		self.y = 0
		self.last_move_time = pygame.time.get_ticks()
		self.attack_speed = 5
		self.weapon = NoWeapon(self)
		self.player = False
		self.target = []
		self.wood = 0
		self.attack_reward = 0  # TODO BUILD THE REWARD SYSTEM USING THE CLASS
		self.rewards = Reward()
		self.actions = ['MOVE_LEFT', 'MOVE_UP', 'MOVE_DOWN', 'MOVE_RIGHT', 'ATTACK_PLAYER', 'IDLE', 'MINE']
		self.total_reward = 0
		self.q_table = {}  # Q-values for state-action pairs
		self.epsilon = 0.5  # Exploration rate
		self.alpha = 0.1    # Learning rate
		self.gamma = 0.9    # Discount factor

	def movement_control(func):
		"""Throttle the NPC movement

		Args:
			func (_type_): _description_
		"""
		def wrapper(self, *args, **kwargs):
			now = pygame.time.get_ticks()

			# Always allow “play_mode” True characters to move after x seconds
			if not getattr(self, 'play_mode', False):
				return func(self, *args, **kwargs)

			# Throttle normal NPCs
			if now - self.last_move_time < self.movement_speed:
				return  # too soon, skip this frame

			# It’s been long enough — update timestamp *before* returning
			self.last_move_time = now
			return func(self, *args, **kwargs)

		return wrapper

	def get_state(self, npc_list, resources_list):

		nearest_enemy = self.get_nearest_npcs(npc_list)
		resources = self.get_nearest_resources(resources_list)
		if nearest_enemy:
			dx = abs(nearest_enemy.x - self.x)
			dy = abs(nearest_enemy.y - self.y)
			x = nearest_enemy.x
			y = nearest_enemy.y
			enemy_health = nearest_enemy.health
		else:
			dx = dy = x = y = enemy_health = -1

		if resources:
			resourcexdx = abs(resources.x - self.x)
			resourceydy = abs(resources.y - self.y)
		else:
			resourcexdx = resourceydy = 0
		

		state = (self.x, self.y, dx, dy, resourcexdx, resourceydy)
		return state

	def get_nearest_npcs(self, npc_list, ally=False):
		if not ally:
			npcs = [npc for npc in npc_list if npc.clan != self.clan and npc.alive]
		else:
			npcs = [npc for npc in npc_list if npc.clan == self.clan and npc.alive]
			# print('npcs : ' + str(npcs))
		if not npcs:
			return None
		npcs.sort(key=lambda npc: ((npc.xPosition - self.xPosition) ** 2 + (npc.yPosition - self.yPosition) ** 2) ** 0.5)
		return npcs[0]
	
	def get_nearest_resources(self, resources_list):
		if not resources_list:
			return None
		resources_list.sort(key=lambda resource: ((resource.xPosition - self.xPosition) ** 2 + (resource.yPosition - self.yPosition) ** 2) ** 0.5)
		return resources_list[0]

	def spawn(self, collision_manager, grid):
		xPosition = random.randint(0, grid.grid_width - 1)
		yPosition = random.randint(0, grid.grid_height - 1 )
		while(collision_manager.grid_colliding_circle(self, xPosition, yPosition, grid)):
			xPosition = random.randint(0, grid.grid_width - 1)
			yPosition = random.randint(0, grid.grid_height - 1 )
		self.x, self.y = xPosition, yPosition
		self.xPosition, self.yPosition = grid.grid_to_pixel(xPosition, yPosition)
		collision_manager.grid.grid[self.y][self.x] = self.grid_character
		collision_manager.object_grid.grid[self.y][self.x] = self

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

	@movement_control
	def act(self, action, collision_manager, npcs, grid):
		""" Given an action it will return a reward
		"""
		reward = 0
		done = False

		dx, dy = 0, 0
		if action == 'MOVE_UP':
			dy -= 1
		elif action == 'MOVE_DOWN':
			dy += 1
		elif action == 'MOVE_LEFT':
			dx -= 1
		elif action == 'MOVE_RIGHT':
			dx += 1

		# Actions: UP, DOWN, LEFT, RIGHT -> Check Collision Check before giving rewards 
		if 0 <= self.y + dy < collision_manager.grid.grid_height and 0 <= self.x + dx < collision_manager.grid.grid_width:
			if collision_manager.grid.grid[self.y + dy][self.x + dx] == ' ':
				if action in ['MOVE_UP', 'MOVE_DOWN', 'MOVE_LEFT', 'MOVE_RIGHT']:
					collision_manager.grid.grid[self.y][self.x] = ' '
					collision_manager.object_grid.grid[self.y][self.x] = None
					self.x = dx + self.x
					self.y = dy + self.y
					self.xPosition, self.yPosition = grid.grid_to_pixel(self.x, self.y)
					collision_manager.grid.grid[self.y][self.x] = self.grid_character
					collision_manager.object_grid.grid[self.y][self.x] = self
					if collision_manager.is_colliding_circle(self, dx, dy):
						# ❌ Can't move, hit something
						reward = -10  # Penalize for bad move
						# print(f"Collision detected at ({self.xPosition}, {self.yPosition}) trying to move {action}")
					else:
						# ✅ Move allowed
						reward = 0.1  # Normal move cost
						# print(f"Moved {action} to ({self.xPosition}, {self.yPosition})")

		#Action: ATTACK
		if action == 'ATTACK_PLAYER':
			# Same as before: attack logic
			nearest_enemy = self.get_nearest_npcs(npcs)
			if nearest_enemy and self._target_is_close(nearest_enemy) and not collision_manager.is_colliding_circle(self, dx, dy):
				self.target = [nearest_enemy]
				self.attack_target(collision_manager)
				nearest_enemy.take_damage(self.weapon.damage, collision_manager.npcs, self)
				reward = 200
			else:
				reward = -5

		#Action: IDLE
		if action == 'IDLE':
			self.health = min(100, self.health + 1)
			reward = -10 

		#Action: MINE
		if action == "MINE":
			# Check if the surrounding environment contains a tree
			# If it does return a reward
			# If it doesn't return 0 or a negative reward
			grid = collision_manager.grid.grid
			height = len(grid)
			width = len(grid[0]) if height > 0 else 0

			def is_tree(y, x):
				return 0 <= y < height and 0 <= x < width and grid[y][x] == 'T'

			if (
				is_tree(self.y + 1, self.x) or
				is_tree(self.y - 1, self.x) or
				is_tree(self.y, self.x + 1) or
				is_tree(self.y, self.x - 1)
			):
				reward = 100
			else:
				reward = 0
			print('SmartNPC is MINING')
			

		self.total_reward += reward
		return reward, done

	def _target_is_close(self, player):
		dx = player.xPosition - self.xPosition
		dy = player.yPosition - self.yPosition
		distance = (dx ** 2 + dy ** 2) ** 0.5
		return distance <= 3 * RADIUS_SIZE

	def is_in_state(self, state_class):
		return isinstance(self.state, state_class)

	def reset(self, collision_manager, grid):
		self.spawn(collision_manager, grid)
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