import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import sys
sys.path.append('../src')
import mase


XScale = int
YScale = int

HEX_OVERLAP = 2/3

@dataclasses.dataclass
class HexGridScaler:
    '''Manages translations between hex coords and pixel space.'''
    screen_size: tuple[mase.Width, mase.Height]
    #hex_size: tuple[mase.Width, mase.Height]
    offset: tuple[mase.Width, mase.Height] # coord -> pixels
    scale: tuple[XScale, YScale] # coord -> pixels
    margin: float = 0.1

    @classmethod
    def from_points(cls,
        screen_size: tuple[mase.Width, mase.Height], 
        points: list[mase.HexCoord],
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
        )
    
    ################################ Scale Conversion ################################
    def hex_to_px(self, hex_coord: mase.HexCoord, flat_top: bool = True) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Convert hex coordinate to pixel coordinate.'''
        return self.cart_to_px(hex_coord.to_cartesian())
    
    def cart_to_px(self, cart_coord: mase.CartCoord) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Convert cartesian coordinate to pixel coordinate.'''
        return (
            round((cart_coord.x - self.offset[0]) * self.scale[0]),
            round((cart_coord.y - self.offset[1]) * self.scale[1]),
        )
    
    ################################ Drawing Functions ################################
    def get_hexagon_points(
        center: tuple[int,int],
        size: float
    ) -> list[tuple[mase.XPixelCoord, mase.YPixelCoord]]:
        '''Draw a hexagon on the screen.'''
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = center[0] + size * math.cos(angle)
            y = center[1] + size * math.sin(angle)
            points.append(((x), (y)))
        return points
        
    ################################ Coordinate Translations ################################
    def get_topleft(self, pos: mase.HexCoord) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Get the top-left corner of the hexagon square.'''
        return pos.x * self.hex_size[0] * HEX_OVERLAP + self.offset[0], pos.y * self.hex_size[1] + self.offset[1]
    
    def get_pos(self, pixel_pos: tuple[mase.XPixelCoord, mase.YPixelCoord]) -> mase.HexCoord:
        '''Get the hex position from pixel coordinates.'''
        return mase.HexCoord(pixel_pos[0] // self.hex_size[0], pixel_pos[1] // self.hex_size[1])
    
    def hex_background_size(self, flat_top: bool = True) -> tuple[mase.Width, mase.Height]:
        '''Size of each hexagon. Different dimensions depending on flat-top or pointy-top orientation.'''
        if flat_top:
            return (2*self.scale[0], mase.SQRT_THREE*self.scale[1])
        else:
            return (mase.SQRT_THREE*self.scale[0], 2*self.scale[1])

    @property
    def hex_size(self) -> tuple[mase.Width, mase.Height]:
        '''Size of each hexagon. Different dimensions depending on flat-top or pointy-top orientation.'''
        return (2*self.scale[0], mase.SQRT_THREE*self.scale[1])


@dataclasses.dataclass
class HexMapViz:
    '''Visualize objects on a hexagonal map.'''

    def draw(self):
        '''Draw the hexagonal map, etc.'''
        pass


def main():
    region = [(o := mase.HexCoord.origin())] + list(o.region(3))
    #positions = origin.region(3)
    scaler = HexGridScaler.from_points((800, 800), region)
    #for pos in positions:
    #    print(pos, viz.coord_to_px(pos))
    print(scaler)
    #print(origin.coords_xy())
    #print(viz.coord_to_px(origin))
    #for coord in list(region)[:3]:
    #    print(coord, viz.coord_to_px(coord), viz.px_to_coord(viz.coord_to_px(coord)))
    #exit()
    with mase.PyGameCtx(size=scaler.screen_size, title='Hexagonal Grid Game') as ctx:
        
        bg_image = ctx.load_image('../data/hex_bg/rock_hexagonal_noborder.png', size=scaler.hex_size)
        

        for i, events in ctx.display_iter(frame_limit=5):
            for event in events:
                print(event)

            ctx.screen.fill((255, 255, 255))


            

            for pos in region:
                ctx.blit_image(bg_image, scaler.coord_to_px(pos))

            for pos in region:
                points = scaler.get_hexagon_points(scaler.coord_to_px(pos), 5)
                ctx.draw_path(points, (255,255,0), width=2, closed=True)
            #ctx.blit_image(bg_image, ctx.center_point())
            #for hex in hex_grid:
            #    pixel_pos = hex_to_pixel(hex, hex_size)
            #    draw_hexagon(screen, (0, 0, 0), pixel_pos, hex_size)
            #sprite_pixel_pos = hex_to_pixel(sprite_pos, hex_size)
            #ctx.screen.blit(bg_image, (10, 10))
            #pygame.display.flip()
            #clock.tick(30)
            #pts = viz.get_hexagon_points(mase.HexCoord.from_origin(), 1000)
            #ctx.draw_polygon((250,250,250), pts)
            #print(pts)


            #print('.', end='', flush=True)
            #time.sleep(0.1)

            #pygame.display.flip()


    print('ended!')



if __name__ == '__main__':
    
    #path = mase.HexCoord.from_origin().a_star(mase.HexCoord(10, 4, -14))
    main()

