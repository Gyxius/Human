from npc import *

class npcFactory:
    def __init__(self, surface):
        self.surface = surface

    def create_npc(self, clan, npc_type = "default"):
        if npc_type == "default":
            return NPC(self.surface, clan = clan)
        elif npc_type == "large":
            return NPC(self.surface, clan = clan, radius = 30)
        elif npc_type == "small":
            return NPC(self.surface, clan = clan, radius = 15)
        else:
            raise ValueError(f"Unknown enemy type: {npc_type}")

