from enum import Enum

class RelationShipType(Enum):
    FAMILY = "Family"
    FRIEND = "Friend"
    COLLEAGUE = "Colleague"
    NEUTRAL = "Neutral"
    DISLIKED = "Disliked"
    ENEMY = "Enemy"
    RIVAL = "Rival"

class Relationship:
    def __init__(self, type: RelationShipType = RelationShipType.NEUTRAL):
        self.type = type
        self.strength = 0.5
        self.interactions = 0
        
    def __str__(self):
        return f"{self.type.value}"

    def __repr__(self):
        strength_desc = "strong" if self.strength > 0.7 else "moderate" if self.strength > 0.4 else "weak"
        return f"{strength_desc} ({self.type.value})"
    
    def improve(self, amount: float = 0.1):
        self.strength = min(1.0, self.strength + amount)
        self.interactions += 1

        if self.type == RelationShipType.DISLIKED and self.strength > 0.6:
            self.type = RelationShipType.NEUTRAL
        elif self.type == RelationShipType.NEUTRAL and self.strength > 0.7:
            self.type = RelationShipType.FRIEND
        elif self.type == RelationShipType.FRIEND and self.strength > 0.9:
            self.type = RelationShipType.COLLEAGUE
            
        return self.type
    
    def deteriorate(self, amount: float = 0.1):
        self.strength = max(0.0, self.strength - amount)
        self.interactions += 1

        if self.type == RelationShipType.COLLEAGUE and self.strength < 0.6:
            self.type = RelationShipType.FRIEND
        elif self.type == RelationShipType.FRIEND and self.strength < 0.4:
            self.type = RelationShipType.NEUTRAL
        elif self.type == RelationShipType.NEUTRAL and self.strength < 0.3:
            self.type = RelationShipType.DISLIKED
        elif self.type == RelationShipType.DISLIKED and self.strength < 0.1:
            self.type = RelationShipType.ENEMY
            
        return self.type