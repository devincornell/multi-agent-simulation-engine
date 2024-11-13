import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import sys
sys.path.append('../src')
import mase

Width = int
Height = int

# hex x,y coordinates
XCoord = int
YCoord = int

# pixel coordinates
XPixelCoord = int
YPixelCoord = int

ColorRGB = tuple[int, int, int]

@dataclasses.dataclass
class PyGameDisplayIterator:
    '''Event loop iterator. Flips at the start of every iteration.'''
    screen: pygame.Surface
    frame_limit: int
    ct: int = 0
    clock: pygame.time.Clock = dataclasses.field(default_factory=pygame.time.Clock)

    def __next__(self):
        '''Flip the display and handle quit events.'''

        # handle quit event
        #for event in pygame.event.get():
        #    if event.type == pygame.QUIT:
        #        pygame.quit()
        #        sys.exit()
        
        pygame.display.flip()
        self.ct += 1

        print('.', end='', flush=True)

        self.clock.tick(self.frame_limit)




@dataclasses.dataclass
class PyGameCtx:
    size: tuple[Width, Height]
    title: typing.Optional[str] = None
    screen: typing.Optional[pygame.Surface] = None

    def __enter__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.title)
        return self

    def __exit__(self, *args):
        pygame.quit()

    def display_iter(self, frame_limit: int = 30) -> PyGameDisplayIterator:
        '''Expose main event loop iterator. Cals pygame.display.flip() after each iteration.'''
        return PyGameDisplayIterator(screen=self.screen, frame_limit=frame_limit)
    
    ################################ Useful Points ################################
    def center_point(self) -> tuple[XPixelCoord, YPixelCoord]:
        '''Get the center point of the screen.'''
        return self.size[0] // 2, self.size[1] // 2

    ################################ Image Loading ################################
    def draw_polygon(self, color: ColorRGB, points: list[tuple[XPixelCoord, YPixelCoord]]) -> None:
        '''Draw a polygon on the screen.'''
        #pygame.draw.rect(self.screen, color, points) # Alt: do something like this?
        return pygame.draw.polygon(self.screen, color, points)

    @staticmethod
    def load_image(path: str|Path, size: tuple[Height, Width] | None = None, **scale_kwargs) -> pygame.Surface:
        im = pygame.image.load(str(path))
        if size is not None:
            return pygame.transform.scale(im, size, **scale_kwargs)
        else:
            return im



HEX_OVERLAP = 0.75

@dataclasses.dataclass
class HexGridViz:
    '''Creates hex grid visualizations.'''
    screen_size: tuple[Width, Height]
    hex_size: tuple[Width, Height]

    @classmethod
    def from_points(cls, screen_size: tuple[Width, Height], points: list[mase.HexPos]) -> typing.Self:
        '''Create hex grid visualization using the points as a reference.'''
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)
        hex_size = (screen_size[0] // max_x, screen_size[1] // max_y)
        return cls(
            screen_size=screen_size, 
            hex_size=hex_size
        )

    ################################ Drawing Functions ################################
    def get_hexagon_points(self, pos: mase.HexPos, size: int) -> list[tuple[XPixelCoord, YPixelCoord]]:
        '''Get the points of a hexagon at the specified position.'''
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = pos.x + size * math.cos(angle)
            y = pos.y + size * math.sin(angle)
            points.append((int(x), int(y)))
        return points
        
    @staticmethod
    def hex_to_pixel(hex, size):
        '''UNTESTED! WRITTEN BY AI'''
        x = size * (3/2 * hex[0])
        y = size * (math.sqrt(3) * (hex[1] + hex[0]/2))
        return (x, y)

    ################################ Coordinate Translations ################################
    def get_center(self, pos: mase.HexPos) -> tuple[XPixelCoord, YPixelCoord]:
        '''Get the pixel center of the hexagon.'''
        topleft = self.get_topleft(pos)
        return topleft[0] + (self.hex_size[0] // 2), topleft[1] + (self.hex_size[1] // 2)
        
    def get_topleft(self, pos: mase.HexPos) -> tuple[XPixelCoord, YPixelCoord]:
        '''Get the top-left corner of the hexagon square.'''
        return pos.x * self.hex_size[0] * HEX_OVERLAP, pos.y * self.hex_size[1] * HEX_OVERLAP
    
    def get_pos(self, pixel_pos: tuple[XPixelCoord, YPixelCoord]) -> mase.HexPos:
        '''Get the hex position from pixel coordinates.'''
        return mase.HexPos(pixel_pos[0] // self.hex_size[0], pixel_pos[1] // self.hex_size[1])




def main():
    # Initialize Pygame
    #pygame.init()
    #w1 = pygame.display.set_mode((800, 600))
    #w2 = pygame.display.set_mode((800, 200))
    #pygame.quit()
    positions = mase.HexPos.from_origin().region(3)
    viz = HexGridViz.from_points((800, 600), positions)

    #sprite_image = pygame.image.load(Path('../data/hex_bg/rock_hexagonal_noborder.png'))
    #sprite_image = pygame.transform.scale(sprite_image, (20, 20))
    
    with PyGameCtx(size=(800, 600), title='Hexagonal Grid Game') as ctx:
        
        bg_image = ctx.load_image('../data/hex_bg/rock_hexagonal_noborder.png', size=viz.hex_size)
        

        while ctx.display_iter(frame_limit=0.5):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            ctx.screen.fill((255, 255, 0))
            #for hex in hex_grid:
            #    pixel_pos = hex_to_pixel(hex, hex_size)
            #    draw_hexagon(screen, (0, 0, 0), pixel_pos, hex_size)
            #sprite_pixel_pos = hex_to_pixel(sprite_pos, hex_size)
            ctx.screen.blit(bg_image, (10, 10))
            #pygame.display.flip()
            #clock.tick(30)
            #pts = viz.get_hexagon_points(mase.HexPos.from_origin(), 1000)
            #ctx.draw_polygon((250,250,250), pts)
            #print(pts)


            print('.', end='', flush=True)
            time.sleep(0.1)


    return
    # Set up display
    width, height = 800, 600
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Hexagonal Grid Game')

    # Set up clock
    clock = pygame.time.Clock()

    # Define hex grid
    hex_size = 40
    hex_grid = [(x, y) for x in range(-5, 6) for y in range(-5, 6) if -5 <= x + y <= 5]

    # Load sprite image
    sprite_image = pygame.image.load(Path('../data/hex_bg/rock_hexagonal_noborder.png'))
    sprite_image = pygame.transform.scale(sprite_image, (hex_size, hex_size))

    # Initial sprite position
    sprite_pos = (0, 0)

    running = True
    while running:

        # Clear screen
        window.fill((255, 255, 255))

        # Draw hex grid
        for hex in hex_grid:
            pixel_pos = hex_to_pixel(hex, hex_size)
            draw_hexagon(window, (0, 0, 0), pixel_pos, hex_size)

        # Draw sprite
        sprite_pixel_pos = hex_to_pixel(sprite_pos, hex_size)
        window.blit(sprite_image, sprite_pixel_pos)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(30)




if __name__ == '__main__':
    
    #path = mase.HexPos.from_origin().a_star(mase.HexPos(10, 4, -14))
    main()

