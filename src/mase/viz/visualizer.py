import typing
import dataclasses


class Visualizer:
    '''Visualizer for hexagonal maps.'''
    def __init__(self, hexmap: HexMap):
        self.hexmap = hexmap
        self._hexmap


