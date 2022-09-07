from importlib.resources import files

DATA = files(__name__)

SPRITES_DIR = DATA / "sprites"

__all__ = ["DATA", "SPRITES_DIR"]
