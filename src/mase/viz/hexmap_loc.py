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
    surfaces: dict[str, pygame.Surface]
    center: tuple[XPixelCoord, YPixelCoord]
    size: tuple[Width, Height]

    @classmethod
    def from_hex_coord(cls, scaler: HexGridScaler, hex_coord: HexCoord):
        '''Create a HexMapLoc from a hex coordinate.'''
        return cls(
            surfaces=dict(),
            center=scaler.hex_to_px(hex_coord),
            size=scaler.hex_background_size(),
        )
    
    ################################ Drawing ################################
    def draw(self, ctx: PyGameCtx, hex_outline: pygame.Color | None = None, width: int = 1):
        '''Draw the hexagon on the screen.'''
        for surf in self.surfaces.values():
            ctx.blit_image(surf, self.center)

        if hex_outline is not None:
            hex_points = self.get_hexagon_points()
            ctx.draw_path(hex_points, hex_outline, width=width, closed=True)
    
    ################################ updating surfaces ################################
    def apply_surfaces(self, apply_func: typing.Callable[[dict[str,pygame.Surface]], dict[str,pygame.Surface]]) -> dict[str,pygame.Surface]:
        '''Apply a function to the surfaces, return the resulting surfaces dictionary.'''
        self.surfaces = apply_func(self.surfaces)
        return self.surfaces

    def insert_scale_surface(self, 
        key: str, 
        surface: pygame.Surface, 
        do_scale: bool = False,
        keep_ratio: bool = True,
        scale_func: typing.Callable[[pygame.Surface, tuple[Width, Height]], pygame.Surface] = pygame.transform.smoothscale,
        **scale_kwargs
    ) -> None:
        '''Insert a surface into the dictionary.'''
        if do_scale:
            surface = PyGameCtx.scale_image(surface, self.size, keep_ratio, scale_func=scale_func, **scale_kwargs)
        self.surfaces[key] = surface

    def get_surfaces(self) -> dict[str, pygame.Surface]:
        '''Get the surfaces.'''
        return self.surfaces
    
    ################################ dunder for updating surfaces ################################
    def __contains__(self, key: str) -> bool:
        '''Check if a surface is in the dictionary.'''
        return key in self.surfaces
    
    def __getitem__(self, key: str) -> pygame.Surface:
        '''Get a surface from the dictionary.'''
        return self.surfaces[key]
    
    def __setitem__(self, key: str, value: pygame.Surface) -> None:
        '''Set a surface in the dictionary.'''
        self.surfaces[key] = value
    
    def __delitem__(self, key: str) -> None:
        '''Delete a surface from the dictionary.'''
        del self.surfaces[key]
    
    ################################ Generating shapes ################################
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
    

