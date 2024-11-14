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

    def draw(self, ctx: PyGameCtx, hex_outline: bool = False) -> None:
        '''Draw the hexagonal map, etc.'''
        for loc in self.locations.values():
            loc.draw(ctx, hex_outline=hex_outline)

    ################################ updating images ################################

    def append_all_images(self, images: list[pygame.Surface], do_scale: bool = False) -> None:
        '''Add an image to the end of the list.'''
        for loc in self.locations.values():
            loc.append_images(images, do_scale=do_scale)

    def append_images(self, image_coords: dict[HexCoord, list[pygame.Surface]], do_scale: bool = False) -> None:
        '''Add an image to the end of the list.'''
        for pos, imgs in image_coords.items():
            self.locations[pos].append_images(imgs, do_scale=do_scale)

    def prepend_all(self, images: list[pygame.Surface], do_scale: bool = False) -> None:
        '''Add an image to the front of the list.'''
        for loc in self.locations.values():
            loc.prepend_images(images, do_scale=do_scale)
    
    def prepend_images(self, image_coords: dict[HexCoord, list[pygame.Surface]], do_scale: bool = False) -> None:
        '''Add an image to the front of the list.'''
        for pos, imgs in image_coords.items():
            self.locations[pos].prepend_images(imgs, do_scale=do_scale)
    
    def update_all_images(self, images: list[pygame.Surface], do_scale: bool = False) -> None:
        '''Set the images to be drawn.'''
        for loc in self.locations.values():
            loc.set_images(images, do_scale=do_scale)

    def update_images(self, image_coords: dict[HexCoord, list[pygame.Surface]], do_scale: bool = False) -> None:
        '''Set the images to be drawn.'''
        for pos, imgs in image_coords.items():
            self.locations[pos].set_images(imgs, do_scale=do_scale)

    ################################ dunder ################################
    def __getitem__(self, key: HexCoord) -> HexMapLoc:
        return self.locations[key]

