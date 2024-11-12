
import random

from .hexmap import HexMap
from .position import HexPos

def random_pathfind_positions(map_size: int, PositionType: type = HexPos, seed: int = 0, percent_avoid: float = 0.25):
    center = PositionType(0,0,0)
    all_positions = center.neighbors(map_size)

    # random sampling for start, end, and blocks
    random.seed(seed)
    avoidset = set(random.sample(all_positions, int(len(all_positions) * percent_avoid)))
    avoidset |= center.fringe(all_positions)
    
    start = random.choice(list(all_positions - avoidset))
    end = random.choice(list(all_positions - avoidset - set([start])))

    return start, end, avoidset

def random_walk(map_size: int, seed: int = 0, include_path: bool = True):
    hmap = HexMap(map_size)
    
    all_positions = hmap.positions()
    
    # random sampling for start, end, and blocks
    random.seed(seed)
    avoidset = set(random.sample(all_positions, len(all_positions) // 4))
    
    start = random.choice(list(all_positions - avoidset))
    end = random.choice(list(all_positions - avoidset - set([start])))
    
    if include_path:
        path = start.shortest_path_dfs(end, avoidset, 2*map_size)
        pathset = set(path)
        for loc in hmap:
            loc.state['start'] = loc.pos == start
            loc.state['end'] = loc.pos == end
            loc.state['passed'] = loc.pos in pathset
            loc.state['blocked'] = loc.pos in avoidset

    loc_info = hmap.get_loc_info()

    return loc_info

def run_test(map_size: int, num_runs: int):
    hmap = HexMap(map_size)
    path_lengths = list()
    for i in range(num_runs):
        start, end, avoidset = test_data(hmap, i)
        path = start.shortest_path_dfs(end, avoidset, 2*map_size)
        path_lengths.append(len(path))
    return start, end, sum(pl for pl in path_lengths if pl is not None)








