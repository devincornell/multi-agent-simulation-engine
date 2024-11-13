import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import sys
sys.path.append('../src')
import mase




def main_complex():

    
    with mase.PyGameCtx(size=(800, 600), title='Hexagonal Grid Game') as ctx:
        
        #bg_image = ctx.load_image('../data/hex_bg/rock_hexagonal_noborder.png', size=viz.hex_size)
        bg_image = pygame.image.load(Path('../data/hex_bg/rock_hexagonal_noborder.png'))
        #bg_image = pygame.transform.scale(bg_image, (20, 20))
        image_rect = bg_image.get_rect()
        image_rect.center = (400, 300)
        print(image_rect)


        #while ctx.display_iter(frame_limit=0.5):
        for i, events in ctx.display_iter(frame_limit=30):
            print(events)

            ctx.screen.fill((255, 255, 255))

            #ctx.screen.fill((255, 255, 0))
            ctx.screen.blit(bg_image, image_rect)

            #pygame.display.flip()
            
            
            #time.sleep(0.1)

            
    #pygame.quit()
    #sys.exit()
    print('this shit is ended')


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

