class TargetManager:
    def __init__(self, npcs, player):
        self.npcs = npcs
        self.player = player

    # def assign_targets(self):
    #     """Assign targets based on proximity, clan, etc."""
    #     for npc in self.npcs:
    #         npc.target = [self.find_nearest_enemy(npc)]

    # def find_nearest_enemy(self, npc):
    #     enemies = [char for char in self.npcs + [self.player] if char.clan != npc.clan and char.health > 0]
    #     if not enemies:
    #         return None
    #     return min(enemies, key=lambda e: self.distance(npc, e))

    # def distance(self, a, b):
    #     return ((a.xPosition - b.xPosition) ** 2 + (a.yPosition - b.yPosition) ** 2) ** 0.5

    def handle_death(self, dead_npc):
        """Reassign targets if a character dies."""
        