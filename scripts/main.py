import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import sys
sys.path.append('../src')
import mase






def main():
    region = [(o := mase.HexCoord.origin())] + list(o.region(10))
    #positions = origin.region(3)
    scaler = mase.HexGridScaler.from_points((800, 800), region)
    viz = mase.HexMapVizualizer.from_points(scaler, region)
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
        viz.prepend_all([bg_image], do_scale=True)

        def handle_mouse_click(event):
            click_pos = pygame.mouse.get_pos()
            print(click_pos)
        
        display = ctx.display_iter(
            frame_limit=30,
            event_callbacks={
                pygame.MOUSEBUTTONDOWN: handle_mouse_click,
            },
        )

        for i, events in display:
            ctx.screen.fill(pygame.Color('white'))

            viz.draw(ctx, hex_outline=True)
            
            # additional drawing
            path = mase.HexCoord.origin().a_star(mase.HexCoord(3, 2, -5), set(region))
            ctx.draw_path(
                points=[viz[p].center for p in path],
                color=pygame.Color('red'), 
                width=3, 
                closed=False
            )

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

