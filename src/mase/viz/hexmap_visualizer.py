import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

from ..types import Width, Height, XPixelCoord, YPixelCoord, ColorRGB

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
    draw_funcs: dict[str, typing.Callable[[PyGameCtx], None]]
    scaler: HexGridScaler

    @classmethod
    def from_points(cls, 
        screen_size: tuple[Width, Height],
        points: list[HexCoord],
        draw_funcs: dict[str, typing.Callable[[PyGameCtx], None]] | None = None,
    ):
        '''Create a hex map from a list of points.'''
        scaler = HexGridScaler.from_points(screen_size, points)
        return cls(
            locations={pos: HexMapLoc.from_hex_coord(scaler, pos) for pos in points},
            draw_funcs=draw_funcs or dict(),
            scaler=scaler,
        )

    def draw(self, 
        ctx: PyGameCtx, 
        hex_outline_color: pygame.Color | None = None,
        bg: pygame.Color | None = None,
    ) -> None:
        '''Draw the hexagonal map, etc.'''
        if bg is not None:
            ctx.screen.fill(pygame.Color('white'))

        for loc in self.locations.values():
            loc.draw(ctx, hex_outline=hex_outline_color)

        for draw_func in self.draw_funcs.values():
            draw_func(ctx)

    ################################ updating images ################################
    def insert_image_all(self, 
        key: str, 
        surface: pygame.Surface, 
        size: tuple[Width, Height] | None = None,
        keep_ratio: bool = True,
        scale_func: typing.Callable[[pygame.Surface, tuple[Width, Height]], pygame.Surface] = pygame.transform.smoothscale,
        **scale_kwargs
    ) -> None:
        '''Insert an image into all locations.'''
        if size is not None:
            surface = PyGameCtx.scale_image(surface, size, keep_ratio, scale_func=scale_func, **scale_kwargs)

        for loc in self.locations.values():
            loc[key] = surface
    
    def delete_image_all(self, key: str, image: pygame.Surface) -> None:
        '''Delete an image from all locations.'''
        for loc in self.locations.values():
            del loc[key]

    def apply_image_all(self, key: str, apply_func: typing.Callable[[dict[str,pygame.Surface]], dict[pygame.Surface]]) -> None:
        '''Apply a function to all surfaces.'''
        for loc in self.locations.values():
            loc.apply_surface(key, apply_func)

    ################################ dunder ################################
    def __getitem__(self, key: HexCoord) -> HexMapLoc:
        return self.locations[key]

