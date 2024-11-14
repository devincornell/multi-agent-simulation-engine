import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path


from ..hexmap import HexCoord, CartCoord, SQRT_THREE
from .hexmap_loc import HexMapLoc
from .hexgrid_scaler import HexGridScaler

if typing.TYPE_CHECKING:
    from ..types import Width, Height, XPixelCoord, YPixelCoord, ColorRGB
from .pygame_context import PyGameCtx
    


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

    def draw(self, ctx: PyGameCtx, hex_outline: pygame.Color | None = None) -> None:
        '''Draw the hexagonal map, etc.'''
        for loc in self.locations.values():
            loc.draw(ctx, hex_outline=hex_outline)

    ################################ updating images ################################
    def insert_image_all(self, key: str, image: pygame.Surface, do_scale: bool = False) -> None:
        '''Insert an image into all locations.'''
        for loc in self.locations.values():
            loc.insert_surface(key, image, do_scale=do_scale)
    
    def delete_image_all(self, key: str, image: pygame.Surface) -> None:
        '''Delete an image from all locations.'''
        for loc in self.locations.values():
            loc.delete_surface(key)

    ################################ dunder ################################
    def __getitem__(self, key: HexCoord) -> HexMapLoc:
        return self.locations[key]

