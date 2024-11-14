import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

from ..hexmap import HexCoord, CartCoord, SQRT_THREE
from .hexgrid_scaler import HexGridScaler
from ..types import Width, Height, XPixelCoord, YPixelCoord, ColorRGB

#if typing.TYPE_CHECKING:
from .pygame_context import PyGameCtx

@dataclasses.dataclass
class HexMapLoc:
    '''State needed to draw a single hex location on the map.'''
    images: list[pygame.Surface]
    center: tuple[XPixelCoord, YPixelCoord]
    size: tuple[Width, Height]

    @classmethod
    def from_hex_coord(cls, scaler: HexGridScaler, hex_coord: HexCoord):
        '''Create a HexMapLoc from a hex coordinate.'''
        return cls(
            images=[],
            center=scaler.hex_to_px(hex_coord),
            size=scaler.hex_background_size(),
        )
    
    ################################ Drawing ################################
    def draw(self, ctx: PyGameCtx, hex_outline: bool = False):
        '''Draw the hexagon on the screen.'''
        for image in self.images:
            ctx.blit_image(image, self.center)

        if hex_outline:
            hex_points = self.get_hexagon_points()
            ctx.draw_path(hex_points, (0,0,0), width=2, closed=True)

    def set_images(self, images: list[pygame.Surface], do_scale: bool = False):
        '''Set the images to be drawn. Not done every iteration.'''
        if do_scale:
            self.images = [pygame.transform.scale(image, self.size) for image in images]
        else:
            self.images = list(images)

    def get_hexagon_points(
        self,
    ) -> list[tuple[XPixelCoord, YPixelCoord]]:
        '''Get hex points on a map..'''
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = self.center[0] + self.size[0] * math.cos(angle)  / 2
            y = self.center[1] + self.size[1] * math.sin(angle) / SQRT_THREE
            points.append((x, y))
        return points
    
    ################################ Other Location Calculations ################################
    def get_topleft(self, pos: HexCoord) -> tuple[XPixelCoord, YPixelCoord]:
        '''Get the top-left corner of the hexagon square.'''
        return pos.x * self.hex_size[0] * HEX_OVERLAP + self.offset[0], pos.y * self.hex_size[1] + self.offset[1]

