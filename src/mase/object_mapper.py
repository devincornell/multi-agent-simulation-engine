from __future__ import annotations
import typing
import dataclasses
import collections


from .coords import BaseCoord
#from .types import AgentID

ObjectID = int

class ObjectIsNotOnMap(Exception):
    '''Exception for when an object is not on the map.'''
    pass

@dataclasses.dataclass(frozen=True)
class ObjectMapper:
    '''Many-to-one mapping mapping of objects to coordinates.
    Description: keeps two dicts: mapping of objects to coordinates and mapping of 
        coordinates to objects. The mapping from coordinates to objects is a defaultdict,
        so that if a coordinate is not in the mapping, it will return an empty set.
    '''
    obj_coords: dict[ObjectID, BaseCoord] = dataclasses.field(default_factory=dict)
    coord_objs: collections.defaultdict[BaseCoord, set[ObjectID]] = dataclasses.field(default_factory=lambda: collections.defaultdict(set))

    ############################## move objects ##############################
    def move_obj(self, obj_id: ObjectID, new_coord: BaseCoord):
        '''Move an object to a new coordinate.'''
        old_coord = self.obj_coords[obj_id]
        self.coord_objs[old_coord].remove(obj_id)
        self.coord_objs[new_coord].add(obj_id)
        self.obj_coords[obj_id] = new_coord

    def remove_obj(self, obj_id: ObjectID):
        '''Remove an object from the mapping.'''
        coord = self.obj_coords[obj_id]
        self.coord_objs[coord].remove(obj_id)
        del self.obj_coords[obj_id]

    def add_obj(self, obj_id: ObjectID, coord: BaseCoord):
        '''Add an object to the mapping.'''
        self.obj_coords[obj_id] = coord
        self.coord_objs[coord].add(obj_id)

    ############################## check the state of the mapping ##############################
    def get_objs(self, coord: BaseCoord) -> set[ObjectID]:
        '''Get all objects at a coordinate.'''
        return self.coord_objs[coord]
    
    def get_coord(self, obj_id: ObjectID) -> BaseCoord:
        '''Get the coordinate of an object.'''
        try:
            return self.obj_coords[obj_id]
        except KeyError:
            raise ObjectIsNotOnMap()
    
    def has_obj(self, obj_id: ObjectID) -> bool:
        '''Check if an object is in the mapping.'''
        return obj_id in self.obj_coords
    
    def has_coord(self, coord: BaseCoord) -> bool:
        '''Check if a coordinate has an object.'''
        return coord in self.coord_objs

    ############################## get all objects and coordinates ##############################
    def objects(self) -> set[ObjectID]:
        '''Get all object ids.'''
        return set(self.obj_coords.keys())
    
    def coords(self) -> set[BaseCoord]:
        '''Get all coordinates.'''
        return set(self.coord_objs.keys())
    