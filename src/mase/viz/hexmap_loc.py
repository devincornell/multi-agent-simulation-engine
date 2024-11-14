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
    def delete_surface(self, key: str, fail_if_dne: bool = False):
        '''Delete a surface from the dictionary.'''
        def apply_func(surfaces: dict[str,pygame.Surface]) -> dict[str,pygame.Surface]:
            surfaces = dict(surfaces)

            if fail_if_dne and key not in surfaces:
                raise ValueError(f'Key {key} does not exist in surfaces.')
            
            del surfaces[key]
            return surfaces
        
        return self.apply_surfaces(apply_func)

    def insert_surface(self, key: str, surface: pygame.Surface, fail_if_exists: bool = False, do_scale: bool = False):
        '''Insert a surface into the dictionary.'''
        if do_scale:
            surface = pygame.transform.scale(surface, self.size)

        def apply_func(surfaces: dict[str,pygame.Surface]) -> dict[str,pygame.Surface]:
            surfaces = dict(surfaces)
            if fail_if_exists and key in surfaces:
                raise ValueError(f'Key {key} already exists in surfaces.')
            surfaces[key] = surface
            return surfaces
        
        return self.apply_surfaces(apply_func)

    def apply_surfaces(self, apply_func: typing.Callable[[dict[str,pygame.Surface]], dict[str,pygame.Surface]]) -> dict[str,pygame.Surface]:
        '''Apply a function to the surfaces, return the resulting surfaces dictionary.'''
        self.surfaces = apply_func(self.surfaces)
        return self.surfaces

    def get_surfaces(self) -> dict[str, pygame.Surface]:
        '''Get the surfaces.'''
        return self.surfaces
    
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
    
    ################################ Other Location Calculations ################################
    def get_topleft(self, pos: HexCoord) -> tuple[XPixelCoord, YPixelCoord]:
        '''Get the top-left corner of the hexagon square.'''
        return pos.x * self.hex_size[0] * HEX_OVERLAP + self.offset[0], pos.y * self.hex_size[1] + self.offset[1]

