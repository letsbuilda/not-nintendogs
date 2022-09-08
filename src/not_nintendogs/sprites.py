import asyncio
import itertools
from collections.abc import Generator
from enum import Enum
from functools import cached_property

import cv2
import numpy as np
import toml
from numpy.typing import NDArray
from nurses_2.widgets.animation import Animation
from nurses_2.widgets.graphic_widget import GraphicWidget
from nurses_2.widgets.graphic_widget_data_structures import Interpolation, Size, Sprite

from .data import SPRITES_DIR


class SpriteSheet(Enum):
    HUSKY = ("husky.png", "dog.toml")

    @cached_property
    def texture(self) -> NDArray:
        """Read the sprite sheet into a numpy array."""
        path = (SPRITES_DIR / self.value[0]).resolve()
        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist.")

        image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

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

    @cached_property
    def metadata(self) -> dict:
        return toml.load(SPRITES_DIR / self.value[1])

    @property
    def info(self) -> dict:
        return self.metadata["info"]

    @property
    def shape(self) -> Size:
        return Size(self.info["width"], self.info["height"])


class AnimSprite(GraphicWidget):
    def __init__(self, info: SpriteSheet, **kwargs):
        super().__init__(size=(32, 40), **kwargs)
        self._sheet = info

        self.frames_idle = list(self._get_anim_frames(0, 4))
        self.frames_liedown = list(self._get_anim_frames(7, 15))
        self.anim_run = Animation.from_sprites(
            self._get_anim_frames(4, 4),
            size_hint=(1, 1),
            pos=(0, 0),
            interpolation=Interpolation.NEAREST,
        )

        # self.texture[:] = 0, 0, 0, 255
        # self.frames_liedown[0].paint(self.texture, pos=(0, 0))

        self.add_widget(self.anim_run)
        self.in_idle = False

    def _get_anim_frames(
        self, row: int, num_frames: int
    ) -> Generator[Sprite, None, None]:
        """Get animation frames_liedown from sprite sheet."""
        shape = self._sheet.shape
        x1 = shape.width * row
        x2 = shape.width * (row + 1)
        for i in range(num_frames):
            y1 = 1 + shape.height * i
            y2 = 1 + shape.height * (i + 1)
            yield Sprite(self._sheet.texture[x1:x2, y1:y2])

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
        for frame in itertools.cycle(self.frames_idle):
            self.texture[:] = 0, 0, 0, 255
            frame.paint(self.texture)
            yield

    def anim_liedown(self):
        for frame in self.frames_liedown:
            self.texture[:] = 0, 0, 0, 255
            frame.paint(self.texture)
            yield
        self.start_animation()
