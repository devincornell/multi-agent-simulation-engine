
import typing

if typing.TYPE_CHECKING:
    from mase.hexmap.hexpos import HexPos



def a_star(
    start: HexPos, 
    goal: HexPos, 
    allowed_pos: typing.Optional[set[HexPos]] = None, 
    max_dist: typing.Optional[int] = None
) -> list[HexPos]:
    '''Compute the A-star algorithm on a hex grid.'''
    if allowed_pos is None:
        allowed_pos = set()

    open_set = [start]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: start.dist(goal)}

    while open_set:
        current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
        open_set.remove(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for neighbor in current.neighbors():
            if neighbor not in allowed_pos:
                continue

            tentative_g_score = g_score[current] + 1

            if max_dist is not None and tentative_g_score > max_dist:
                continue

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + neighbor.dist(goal)
                if neighbor not in open_set:
                    open_set.append(neighbor)

    return []
