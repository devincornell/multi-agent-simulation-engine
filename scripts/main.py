import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import sys
sys.path.append('../src')
import mase


def event_factory(
    viz: mase.HexMapVizualizer, 
    ctx: mase.PyGameCtx,
    available: set[mase.HexCoord],
    region: list[mase.HexCoord],
    red_withsword: pygame.Surface,
) -> dict[str, typing.Callable[[pygame.event.Event], None]]:
    '''Create a dictionary of event call backs.'''
    def handle_mouse_click(event, key: str = 'character', path_key_base: str = 'path'):
        click_pos = pygame.mouse.get_pos()
        pos = viz.scaler.px_to_hex(click_pos).closest(region)
        print('clicked:', pos)
        if pos in available:
            if key in viz[pos]:
                del viz[pos][key] # remove if exists
            else:
                #viz[pos][key] = red_withsword # add if does not
                viz[pos].insert_scale_surface(key, red_withsword, do_scale=True)

            path_key = (path_key_base, pos)
            if path_key in viz.draw_funcs:
                del viz.draw_funcs[path_key]
            else:
                try:    
                    path = mase.HexCoord.origin().a_star(pos, available)
                    points = [viz[p].center for p in path]
                    def draw_path_func(ctx: mase.PyGameCtx):
                        ctx.draw_path(
                            points=points,
                            color=pygame.Color('red'), 
                            width=3, 
                            closed=False
                        )
                    viz.draw_funcs[path_key] = draw_path_func
                except (mase.NoPathFound, mase.SourceIsSameAsDest):
                    pass

    return {
        pygame.MOUSEBUTTONDOWN: handle_mouse_click,
    }


def main():
    region = [(o := mase.HexCoord.origin())] + list(o.region(5))
    blocked = set([
        mase.HexCoord(0, 1, -1),
        mase.HexCoord(1, 0, -1),
        mase.HexCoord(1, -1, 0),
        mase.HexCoord(0, -1, 1),
    ])
    available = set(region) - blocked

    # make visualizer and scaler
    viz = mase.HexMapVizualizer.from_points((800, 800), region)

    red_nosword = pygame.image.load('../data/sprites/redknight_nosword.png')
    red_withsword = pygame.image.load('../data/sprites/redknight_withsword.png')
    bg_image = pygame.image.load('../data/hex_bg/rock_hexagonal_noborder.png')

    for pos, loc in viz.locations.items():
        if pos in available:
            #print(loc.size)
            loc.insert_scale_surface('bg', bg_image, do_scale=True)


    with mase.PyGameCtx(size=viz.scaler.screen_size, title='Hexagonal Grid Game') as ctx:
        display_loop = ctx.display_iter(
            frame_limit=30,
            event_callbacks=event_factory(
                viz=viz, 
                ctx=ctx, 
                available=available, 
                region=region,
                red_withsword=red_withsword,
            ),
        )

        for i, events in display_loop:
            
            viz.draw(
                ctx = ctx, 
                hex_outline_color=pygame.Color('green'),
                bg=pygame.Color('black'),
            )
            
            # additional drawing
            #path = mase.HexCoord.origin().a_star(mase.HexCoord(3, 2, -5), set(region))
            #ctx.draw_path(
            #    points=[viz[p].center for p in path],
            #    color=pygame.Color('red'), 
            #    width=3, 
            #    closed=False
            #)

            #for pos in region:
            #    ctx.blit_image(bg_image, scaler.coord_to_px(pos))

            #for pos in region:
            #    points = scaler.get_hexagon_points(scaler.coord_to_px(pos), 5)
            #    ctx.draw_path(points, (255,255,0), width=2, closed=True)
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

