import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import sys
sys.path.append('../src')
import mase





HEX_OVERLAP = 0.75

@dataclasses.dataclass
class HexGridViz:
    '''Creates hex grid visualizations.'''
    screen_size: tuple[mase.Width, mase.Height]
    hex_size: tuple[mase.Width, mase.Height]
    offset: tuple[mase.Width, mase.Height] | None = None # extent to which coordinate system is offset from screen position

    @classmethod
    def from_points(cls, screen_size: tuple[mase.Width, mase.Height], points: list[mase.HexCoord]) -> typing.Self:
        '''Create hex grid visualization using the points as a reference.'''
        
        # identify bounds in coordinate space
        min_x, max_x = min(p.x for p in points), max(p.x for p in points)
        min_y, max_y = min(p.y for p in points), max(p.y for p in points)



        hex_size = (screen_size[0] // max_x, screen_size[1] // max_y)
        o = cls(
            screen_size=screen_size, 
            hex_size=hex_size,
        )
        o.offset = (screen_size[0] - hex_size[0] * max_x, screen_size[1] - hex_size[1] * max_y)
        return o

    ################################ Drawing Functions ################################
    def get_hexagon_points(self, pos: mase.HexCoord, size: int) -> list[tuple[mase.XPixelCoord, mase.YPixelCoord]]:
        '''Get the points of a hexagon at the specified position.'''
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = pos.x + size * math.cos(angle)
            y = pos.y + size * math.sin(angle)
            points.append(((x), (y)))
        return points
        
    @staticmethod
    def hex_to_pixel(hex, size):
        '''UNTESTED! WRITTEN BY AI'''
        x = size * (3/2 * hex[0])
        y = size * (math.sqrt(3) * (hex[1] + hex[0]/2))
        return (x, y)

    ################################ Coordinate Translations ################################
    def get_center(self, pos: mase.HexCoord) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Get the pixel center of the hexagon.'''
        topleft = self.get_topleft(pos)
        return topleft[0] + (self.hex_size[0] // 2), topleft[1] + (self.hex_size[1] // 2)
        
    def get_topleft(self, pos: mase.HexCoord) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Get the top-left corner of the hexagon square.'''
        return pos.x * self.hex_size[0] * HEX_OVERLAP + self.offset[0], pos.y * self.hex_size[1] + self.offset[1]
    
    def get_pos(self, pixel_pos: tuple[mase.XPixelCoord, mase.YPixelCoord]) -> mase.HexCoord:
        '''Get the hex position from pixel coordinates.'''
        return mase.HexCoord(pixel_pos[0] // self.hex_size[0], pixel_pos[1] // self.hex_size[1])




def main():
    positions = mase.HexCoord.from_origin().region(3)
    viz = HexGridViz.from_points((800, 600), positions)
    
    with mase.PyGameCtx(size=viz.screen_size, title='Hexagonal Grid Game') as ctx:
        
        bg_image = ctx.load_image('../data/hex_bg/rock_hexagonal_noborder.png', size=viz.hex_size)
        

        for i, events in ctx.display_iter(frame_limit=5):
            print(events)
            for event in events:
                print(event)

            ctx.screen.fill((255, 255, 255))

            for pos in positions:
                ctx.blit_image(bg_image, viz.get_center(pos))
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

