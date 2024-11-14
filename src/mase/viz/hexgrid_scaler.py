import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path


from ..hexmap import HexCoord, CartCoord, SQRT_THREE

from ..types import Width, Height, XPixelCoord, YPixelCoord, ColorRGB



XScale = int
YScale = int

HEX_OVERLAP = 2/3

@dataclasses.dataclass
class HexGridScaler:
    '''Manages translations between game coordinates (hex or cartesian) and pixel space.
    Description:
        main parameters: offset and scale
        coord -> pixel: (coord - offset) * scale
        pixel -> coord: (pixel / scale) + offset
    '''
    screen_size: tuple[Width, Height]
    offset: tuple[Width, Height] # coord -> pixels
    scale: tuple[XScale, YScale] # coord -> pixels
    flat_top: bool = True
    margin: float = 0.1

    @classmethod
    def from_points(cls,
        screen_size: tuple[Width, Height], 
        points: list[HexCoord],
        **kwargs,
    ) -> typing.Self:
        '''Create hex grid visualization using the points as a reference.'''
        
        # identify bounds in coordinate space
        xy_points = [p.to_cartesian() for p in points]
        min_x, max_x = min(p.x for p in xy_points), max(p.x for p in xy_points)
        min_y, max_y = min(p.y for p in xy_points), max(p.y for p in xy_points)
        #print(min_x, max_x, min_y, max_y)
        
        return cls(
            screen_size=screen_size, 
            offset=(min_x, min_y),
            scale=(
                (screen_size[0] // (max_x - min_x)),
                (screen_size[1] // (max_y - min_y)),
            ),
            **kwargs,
        )
    
    ################################ Scale Conversion ################################
    def hex_to_px(self, hex_coord: HexCoord) -> tuple[XPixelCoord, YPixelCoord]:
        '''Convert hex coordinate to pixel coordinate.'''
        return self.cart_to_px(hex_coord.to_cartesian())
    
    def cart_to_px(self, cart_coord: CartCoord) -> tuple[XPixelCoord, YPixelCoord]:
        '''Convert cartesian coordinate to pixel coordinate.'''
        return (
            round((cart_coord.x - self.offset[0]) * self.scale[0]),
            round((cart_coord.y - self.offset[1]) * self.scale[1]),
        )
    
    def px_to_hex(self, pixel_pos: tuple[XPixelCoord, YPixelCoord]) -> HexCoord:
        '''Convert pixel coordinate to hex coordinate.'''
        return self.px_to_cart(pixel_pos).to_hex(flat_top=self.flat_top)
    
    def px_to_cart(self, pixel_pos: tuple[XPixelCoord, YPixelCoord]) -> CartCoord:
        '''Convert pixel coordinate to cartesian coordinate.'''
        return CartCoord(
            x = pixel_pos[0] / self.scale[0] + self.offset[0],
            y = pixel_pos[1] / self.scale[1] + self.offset[1],
        )
            
    ################################ Coordinate Translations ################################
    def get_pos(self, pixel_pos: tuple[XPixelCoord, YPixelCoord]) -> HexCoord:
        '''Get the hex position from pixel coordinates.'''
        return HexCoord(pixel_pos[0] // self.hex_size[0], pixel_pos[1] // self.hex_size[1])
    
    def hex_background_size(self) -> tuple[Width, Height]:
        '''Size of each hexagon. Different dimensions depending on flat-top or pointy-top orientation.'''
        if self.flat_top:
            return (2*self.scale[0], SQRT_THREE*self.scale[1])
        else:
            return (SQRT_THREE*self.scale[0], 2*self.scale[1])

    @property
    def hex_size(self) -> tuple[Width, Height]:
        '''Size of each hexagon. Different dimensions depending on flat-top or pointy-top orientation.'''
        return (2*self.scale[0], SQRT_THREE*self.scale[1])