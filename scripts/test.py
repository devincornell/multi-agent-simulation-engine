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

def main_complex():

    
    with PyGameCtx(size=(800, 600), title='Hexagonal Grid Game') as ctx:
        
        #bg_image = ctx.load_image('../data/hex_bg/rock_hexagonal_noborder.png', size=viz.hex_size)
        bg_image = pygame.image.load(Path('../data/hex_bg/rock_hexagonal_noborder.png'))
        #bg_image = pygame.transform.scale(bg_image, (20, 20))
        image_rect = bg_image.get_rect()
        image_rect.center = (400, 300)


        #while ctx.display_iter(frame_limit=0.5):
        while ctx.display_iter(frame_limit=30):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            ctx.screen.fill((255, 255, 255))

            #ctx.screen.fill((255, 255, 0))
            ctx.screen.blit(bg_image, image_rect)

            pygame.display.flip()
            
            time.sleep(0.1)

            
    pygame.quit()
    sys.exit()



def main_simple():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Display Image')

    # Load the image
    image = pygame.image.load('../data/hex_bg/rock_hexagonal_noborder.png')

    # Get the image rect
    image_rect = image.get_rect()

    # Center the image
    image_rect.center = (400, 300)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with white
        screen.fill((255, 255, 255))

        # Blit the image to the screen
        screen.blit(image, image_rect)

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()



if __name__ == '__main__':
    
    #path = mase.HexPos.from_origin().a_star(mase.HexPos(10, 4, -14))
    main_complex()

