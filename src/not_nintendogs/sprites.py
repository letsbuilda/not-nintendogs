import asyncio
import itertools
from enum import Enum
from functools import cached_property
from os import PathLike
from pathlib import Path

import cv2
import numpy as np
import toml
from nurses_2.widgets.graphic_widget import GraphicWidget
from nurses_2.widgets.graphic_widget_data_structures import Sprite

from .data import SPRITES_DIR
from .logger import log


class SpriteInfo(Enum):
    DOG = "dog.toml"


class AnimSprite(GraphicWidget):
    def __init__(self, sprite_sheet: str | PathLike, info: SpriteInfo, **kwargs):
        self.sprite_sheet = (SPRITES_DIR / Path(sprite_sheet)).absolute()
        if not self.sprite_sheet.exists():
            raise FileNotFoundError(f"{self.sprite_sheet} does not exist.")
        self.sprite_metadata = toml.load(SPRITES_DIR / info.value)
        self.sprite_info = self.sprite_metadata["info"]
        w, h = self.sprite_info["width"], self.sprite_info["height"]
        log.info(f"Sprite size: {w} x {h}")
        log.info(f"Array shape: {(s := self.sheet_texture.shape)} ({s[0]})")
        row = 0
        self.idle_frames = [
            Sprite(
                self.sheet_texture[
                    32 * row : 32 * (row + 1), 1 + (40 * i) : 1 + (40 * (i + 1))
                ]
            )
            for i in range(2)  # 4
        ]
        row = 7
        self.frames = [
            Sprite(
                self.sheet_texture[
                    32 * row : 32 * (row + 1), 1 + (40 * i) : 1 + (40 * (i + 1))
                ]
            )
            for i in range(14)  # 15
        ]

        super().__init__(size=(32, 40), **kwargs)
        self.texture[:] = 0, 0, 0, 255
        self.frames[0].paint(self.texture, pos=(0, 0))
        self.in_idle = False

    def start_animation(self):
        self.in_idle = True

        async def _anim():
            for _ in self.anim_idle():
                if not self.in_idle:
                    break
                await asyncio.sleep(0.18)

        asyncio.create_task(_anim())

    def play_liedown(self):
        self.in_idle = False

        async def _anim():
            for _ in self.anim_liedown():
                await asyncio.sleep(0.18)

        asyncio.create_task(_anim())

    def anim_idle(self):
        for frame in itertools.cycle(self.idle_frames):
            self.texture[:] = 0, 0, 0, 255
            frame.paint(self.texture)
            yield

    def anim_liedown(self):
        for frame in self.frames:
            self.texture[:] = 0, 0, 0, 255
            frame.paint(self.texture)
            yield
        self.start_animation()

    @cached_property
    def sheet_texture(self):
        """
        Read the sprite sheet into a numpy array.
        """
        image = cv2.imread(str(self.sprite_sheet), cv2.IMREAD_UNCHANGED)

        if image.dtype == np.dtype(np.uint16):
            image = (image // 257).astype(np.uint8)
        elif image.dtype == np.dtype(np.float32):
            image = (image * 255).astype(np.uint8)

        # Add an alpha channel if there isn't one.
        h, w, c = image.shape
        if c == 3:
            default_alpha_channel = np.full((h, w, 1), 255, dtype=np.uint8)
            image = np.dstack((image, default_alpha_channel))

        texture = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)

        return texture
