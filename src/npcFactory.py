from npc import *

class npcFactory:
    def __init__(self, surface):
        self.surface = surface

    def create_npc(self, clan, npc_type = "default"):
        if npc_type == "default":
            return NPC(self.surface, vision = 1000, clan = clan)
        elif npc_type == "large":
            # The big one walks slowly but has a larger vision and has a higher attack damage but a low attack speed
            return NPC(self.surface, clan = clan, radius = 30, speed = 0.5, vision = 1000, damage = 20)
        elif npc_type == "small":
            # The small one walks fastly but has a lower vision and has a lower attack damage but high attack speed
            return NPC(self.surface, clan = clan, radius = 15, speed = 1.5, vision = 1000, damage = 5)
        else:
            raise ValueError(f"Unknown enemy type: {npc_type}")

