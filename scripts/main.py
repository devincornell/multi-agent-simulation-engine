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
    flat_top: bool = True
    margin: float = 0.1

    @classmethod
    def from_points(cls,
        screen_size: tuple[mase.Width, mase.Height], 
        points: list[mase.HexCoord],
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
    def hex_to_px(self, hex_coord: mase.HexCoord) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Convert hex coordinate to pixel coordinate.'''
        return self.cart_to_px(hex_coord.to_cartesian())
    
    def cart_to_px(self, cart_coord: mase.CartCoord) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Convert cartesian coordinate to pixel coordinate.'''
        return (
            round((cart_coord.x - self.offset[0]) * self.scale[0]),
            round((cart_coord.y - self.offset[1]) * self.scale[1]),
        )
            
    ################################ Coordinate Translations ################################
    def get_pos(self, pixel_pos: tuple[mase.XPixelCoord, mase.YPixelCoord]) -> mase.HexCoord:
        '''Get the hex position from pixel coordinates.'''
        return mase.HexCoord(pixel_pos[0] // self.hex_size[0], pixel_pos[1] // self.hex_size[1])
    
    def hex_background_size(self) -> tuple[mase.Width, mase.Height]:
        '''Size of each hexagon. Different dimensions depending on flat-top or pointy-top orientation.'''
        if self.flat_top:
            return (2*self.scale[0], mase.SQRT_THREE*self.scale[1])
        else:
            return (mase.SQRT_THREE*self.scale[0], 2*self.scale[1])

    @property
    def hex_size(self) -> tuple[mase.Width, mase.Height]:
        '''Size of each hexagon. Different dimensions depending on flat-top or pointy-top orientation.'''
        return (2*self.scale[0], mase.SQRT_THREE*self.scale[1])


@dataclasses.dataclass
class HexMapLoc:
    '''State needed to draw a single hex location on the map.'''
    images: list[pygame.Surface]
    center: tuple[mase.XPixelCoord, mase.YPixelCoord]
    size: tuple[mase.Width, mase.Height]

    @classmethod
    def from_hex_coord(cls, scaler: HexGridScaler, hex_coord: mase.HexCoord):
        '''Create a HexMapLoc from a hex coordinate.'''
        return cls(
            images=[],
            center=scaler.hex_to_px(hex_coord),
            size=scaler.hex_background_size(),
        )
    
    ################################ Drawing ################################
    def draw(self, ctx: mase.PyGameCtx, hex_outline: bool = False):
        '''Draw the hexagon on the screen.'''
        for image in self.images:
            ctx.blit_image(image, self.center)

        if hex_outline:
            hex_points = self.get_hexagon_points()
            ctx.draw_path(hex_points, (0,0,0), width=2, closed=True)

    def set_images(self, images: list[pygame.Surface], do_scale: bool = False):
        '''Set the images to be drawn. Not done every iteration.'''
        if do_scale:
            self.images = [pygame.transform.scale(image, self.size) for image in images]
        else:
            self.images = list(images)

    def get_hexagon_points(
        self,
    ) -> list[tuple[mase.XPixelCoord, mase.YPixelCoord]]:
        '''Get hex points on a map..'''
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = self.center[0] + self.size[0] * math.cos(angle)  / 2
            y = self.center[1] + self.size[1] * math.sin(angle) / mase.SQRT_THREE
            points.append((x, y))
        return points
    
    ################################ Other Location Calculations ################################
    def get_topleft(self, pos: mase.HexCoord) -> tuple[mase.XPixelCoord, mase.YPixelCoord]:
        '''Get the top-left corner of the hexagon square.'''
        return pos.x * self.hex_size[0] * HEX_OVERLAP + self.offset[0], pos.y * self.hex_size[1] + self.offset[1]


@dataclasses.dataclass
class HexMapVizualizer:
    '''Visualize objects on a hexagonal map.'''
    locations: dict[mase.HexCoord, HexMapLoc]
    #scaler: HexGridScaler

    @classmethod
    def from_points(cls, scaler: HexGridScaler, points: list[mase.HexCoord]):
        '''Create a hex map from a list of points.'''
        return cls(
            locations={pos: HexMapLoc.from_hex_coord(scaler, pos) for pos in points},
        )

    def draw(self, ctx: mase.PyGameCtx, hex_outline: bool = False) -> None:
        '''Draw the hexagonal map, etc.'''
        for loc in self.locations.values():
            loc.draw(ctx, hex_outline=hex_outline)

    def update_images(self, image_coords: dict[mase.HexCoord, list[pygame.Surface]], do_scale: bool = False):
        '''Set the images to be drawn.'''
        for pos, imgs in image_coords.items():
            self.locations[pos].set_images(imgs, do_scale=do_scale)

    def __getitem__(self, key: mase.HexCoord) -> HexMapLoc:
        return self.locations[key]



def main():
    region = [(o := mase.HexCoord.origin())] + list(o.region(10))
    #positions = origin.region(3)
    scaler = HexGridScaler.from_points((800, 800), region)
    viz = HexMapVizualizer.from_points(scaler, region)
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
                if event.type == pygame.MOUSEBUTTONUP:
                    click_pos = pygame.mouse.get_pos()
                print(event)

            ctx.screen.fill((255, 255, 255))

            viz.draw(ctx, hex_outline=True)
            
            # additional drawing
            path = mase.HexCoord.origin().a_star(mase.HexCoord(3, 2, -5), set(region))
            ctx.draw_path(
                points=[viz[p].center for p in path],
                color=(255,0,0), 
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

