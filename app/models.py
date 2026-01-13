import enum

# MaterialType enum (used in schemas)
class MaterialType(str, enum.Enum):
    GEMSTONE = "GEMSTONE"
    METAL = "METAL"
    OTHER = "OTHER"


# ProductType enum (used in schemas)
class ProductType(str, enum.Enum):
    RING = "RING"
    NECKLACE = "NECKLACE"
    EARRING = "EARRING"
    BRACELET = "BRACELET"