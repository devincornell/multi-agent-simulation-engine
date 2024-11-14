from __future__ import annotations
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
    clock: pygame.time.Clock
    event_callbacks: dict[pygame.event.EventType, typing.Callable]
    ct: int = 0

    @classmethod
    def from_context(
        cls,
        ctx: PyGameCtx,
        frame_limit: int,
        event_callbacks: dict[pygame.event.EventType, typing.Callable[[pygame.event.Event], None]],
    ) -> PyGameDisplayIterator:
        '''Create a display iterator from a context.'''

        # allow any event call backs, use 
        use_event_callbacks = {**{pygame.QUIT: cls.default_quit_event}, **event_callbacks}

        return cls(
            screen=ctx.screen, 
            frame_limit=frame_limit,
            clock = pygame.time.Clock(),
            event_callbacks=use_event_callbacks,
        )

    def __iter__(self):
        self.ct = 0
        return self

    def __next__(self) -> tuple[int, list[pygame.event.Event]]:
        '''Flip the display and handle quit events.'''

        # handle quit event
        events = list()
        for event in pygame.event.get():
            if event.type in self.event_callbacks:
                self.event_callbacks[event.type](event)
            else:
                events.append(event)
        
        pygame.display.flip()
        self.clock.tick(self.frame_limit)

        self.ct += 1
        return self.ct, events
    
    @classmethod
    def default_quit_event(cls, event: pygame.event.Event) -> None:
        '''Default quit event callback.'''
        pygame.quit()
        #sys.exit()
        raise StopIteration




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

    def display_iter(
        self, 
        frame_limit: int = 30,
        event_callbacks: dict[pygame.event.EventType, typing.Callable[[pygame.event.Event], None]] | None = None,                 
    ) -> PyGameDisplayIterator:
        '''Expose main event loop iterator. Cals pygame.display.flip() after each iteration.'''
        return PyGameDisplayIterator.from_context(
            ctx=self, 
            frame_limit=frame_limit,
            event_callbacks=event_callbacks or dict(),
        )
    
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

    ################################ Utility Methods ################################
    @classmethod
    def load_image(
        cls,
        path: str|Path, 
        size: tuple[Height, Width] | None = None, 
        keep_ratio: bool = True,
        **scale_kwargs
    ) -> pygame.Surface:
        im = pygame.image.load(str(path))
        if size is not None:
            im = cls.scale_image(im, size, keep_ratio, **scale_kwargs)
        return im

    @classmethod
    def scale_image(
        cls,
        surface: pygame.Surface, 
        size: tuple[Height, Width], 
        keep_ratio: bool = True,
        scale_func: typing.Callable[[pygame.Surface, tuple[Width, Height]], pygame.Surface] = pygame.transform.smoothscale,
        **scale_kwargs
    ) -> pygame.Surface:
        '''Scale an image.'''
        if keep_ratio:
            ratio = surface.get_width() / surface.get_height()
            w, h = size
            if w / h > ratio:
                size = (int(h * ratio), h)
            else:
                size = (w, int(w / ratio))
            return scale_func(surface, size, **scale_kwargs)
        else:
            return scale_func(surface, size, **scale_kwargs)

