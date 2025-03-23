# The goal is to create a class Attack that will allow the player, npc, to attack each other
# There will be multiple types of attacks, like using a spell, using a weapon, or barehands

class Attack():
    """Base class for weapons."""
    def __init__(self, owner, damage, attack_size):
        self.owner = owner  # The player or NPC using this weapon
        self.damage = damage
        self.attack_size = attack_size  # Width & height of attack
        self.active = False  # Attack is inactive until triggered
        self.attack_rect = None  # The area where the attack happens
