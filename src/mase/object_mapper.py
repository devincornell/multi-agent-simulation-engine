from __future__ import annotations
import typing
import dataclasses
import collections


from .coords import BaseCoord
#from .types import AgentID

ObjectID = int



@dataclasses.dataclass(frozen=True)
class ObjectMapper:
    '''Many-to-one mapping mapping of objects to coordinates.
    '''
    obj_coords: dict[ObjectID, BaseCoord] = dataclasses.field(default_factory=dict)
    coord_objs: dict[BaseCoord, set[ObjectID]] = dataclasses.field(default_factory=lambda: collections.defaultdict(set))

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

    def get_objs(self, coord: BaseCoord) -> set[ObjectID]:
        '''Get all objects at a coordinate.'''
        return self.coord_objs[coord]
    
    def get_coord(self, obj_id: ObjectID) -> BaseCoord:
        '''Get the coordinate of an object.'''
        return self.obj_coords[obj_id]

    def objects(self) -> set[ObjectID]:
        '''Get all object ids.'''
        return set(self.obj_coords.keys())
    
    def coords(self) -> set[BaseCoord]:
        '''Get all coordinates.'''
        return set(self.coord_objs.keys())
    