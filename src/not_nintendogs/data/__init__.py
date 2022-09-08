from importlib.resources import files
from pathlib import Path

DATA = files(__name__)

SPRITES_DIR = Path(str(DATA / "sprites"))

__all__ = ["DATA", "SPRITES_DIR"]
