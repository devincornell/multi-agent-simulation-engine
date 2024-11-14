import sys
import pygame
import typing
import dataclasses
from pathlib import Path

from ..types import Width, Height, XPixelCoord, YPixelCoord, ColorRGB


@dataclasses.dataclass
class PyGameDisplayIterator:
    '''Event loop iterator. Flips at the start of every iteration.'''
    screen: pygame.Surface
    frame_limit: int
    ct: int = 0
    clock: pygame.time.Clock = dataclasses.field(default_factory=pygame.time.Clock)

    def __iter__(self):
        return self

    def __next__(self):
        '''Flip the display and handle quit events.'''

        # handle quit event
        events = list()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #sys.exit()
                raise StopIteration
            else:
                events.append(event)
        
        pygame.display.flip()
        self.clock.tick(self.frame_limit)

        self.ct += 1
        return self.ct, events




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
    def draw_path(self, points: list[tuple[XPixelCoord, YPixelCoord]], color: ColorRGB, width: int = 1, closed: bool = False) -> None:
        '''Draw a path on the screen. Wrapper over pygame.draw.lines. '''
        return pygame.draw.lines(
            surface=self.screen, 
            color=color, 
            closed=closed, 
            points=points, 
            width=width
        )

    def draw_polygon(self, points: list[tuple[XPixelCoord, YPixelCoord]], color: ColorRGB, width: int = 1) -> None:
        '''Draw a polygon on the screen.'''
        #pygame.draw.rect(self.screen, color, points) # Alt: do something like this?
        return pygame.draw.polygon(self.screen, color, points, width=width)
    
    def blit_image(self, image: pygame.Surface, center: tuple[XPixelCoord, YPixelCoord]) -> None:
        '''Blit an image at a position.'''
        image_rect = image.get_rect()
        image_rect.center = center
        return self.screen.blit(image, image_rect)
    




    @staticmethod
    def load_image(
        path: str|Path, 
        size: tuple[Height, Width] | None = None, 
        **scale_kwargs
    ) -> pygame.Surface:
        im = pygame.image.load(str(path))
        if size is not None:
            return pygame.transform.scale(im, size, **scale_kwargs)
        else:
            return im
