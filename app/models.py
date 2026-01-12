import enum

# MaterialType enum (used in schemas)
class MaterialType(str, enum.Enum):
    GEMSTONE = "GEMSTONE"
    METAL = "METAL"
    OTHER = "OTHER"