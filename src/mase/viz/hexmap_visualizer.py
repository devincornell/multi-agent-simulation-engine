import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path


from ..hexmap import HexCoord, CartCoord, SQRT_THREE
from .hexmap_loc import HexMapLoc

if typing.TYPE_CHECKING:
    from ..types import Width, Height, XPixelCoord, YPixelCoord, ColorRGB
    from .pygame_context import PyGameCtx
    from .hexgrid_scaler import HexGridScaler


@dataclasses.dataclass
class HexMapVizualizer:
    '''Visualize objects on a hexagonal map.'''
    locations: dict[HexCoord, HexMapLoc]
    #scaler: HexGridScaler

    @classmethod
    def from_points(cls, scaler: HexGridScaler, points: list[HexCoord]):
        '''Create a hex map from a list of points.'''
        return cls(
            locations={pos: HexMapLoc.from_hex_coord(scaler, pos) for pos in points},
        )

    def draw(self, ctx: PyGameCtx, hex_outline: bool = False) -> None:
        '''Draw the hexagonal map, etc.'''
        for loc in self.locations.values():
            loc.draw(ctx, hex_outline=hex_outline)

    def update_images(self, image_coords: dict[HexCoord, list[pygame.Surface]], do_scale: bool = False):
        '''Set the images to be drawn.'''
        for pos, imgs in image_coords.items():
            self.locations[pos].set_images(imgs, do_scale=do_scale)

    def __getitem__(self, key: HexCoord) -> HexMapLoc:
        return self.locations[key]

