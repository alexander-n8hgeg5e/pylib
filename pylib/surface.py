from math import inf,sqrt
__doc__='''flat surfaces'''

def point_is_in_direction_from_point(p0,direction,p1):
    # delta x , delta y
    p = (p1[0]-p0[0], p1[1]-p0[1])
    try:
        tan=p[1]/p[0]
    except ZeroDivisionError:
        if direction in ('left', 'right'):
            return False
        elif direction in ('up', 'down'):
            return True
    return p[1]/p[0] <= 1

def distance_of_points(p0,p1):
    p = (p1[0]-p0[0], p1[1]-p0[1])
    return sqrt(p[0]**2+p[1]**2)

def pos_in_2D_interval(pos,interval):
    return val_in_interval(pos[0],interval[0]) and val_in_interval(pos[1],interval[1])

def val_in_interval(v,interval):
    return interval[0] < v < interval[1]

def get_point_index_in_direction_from_point(
    point, direction, all_the_other_points,
    search_area={"interval_x":(-inf,+inf),'interval_y':(-inf,+inf)}
                                     ):
    positions = all_the_other_points
    positions.append(point)
    lowest_distance = inf
    lowest_distance_index = None
    own_pos = point
    interval_x = search_area['interval_x']
    interval_y = search_area['interval_y']
    for i in range(len(positions)):
        p=positions[i]
        if pos_in_2D_interval(p,(interval_x,interval_y)):
            if direction in ('right'):
                if p[0] > own_pos[0] and point_is_in_direction_from_point(own_pos,direction,p):
                    d = distance_of_points(own_pos,p)
                    if d < lowest_distance:
                        lowest_distance=d
                        lowest_distance_index = i
                else:
                    p = None
            elif direction in ('down'):
                if p[1] > own_pos[1] and point_is_in_direction_from_point(own_pos,direction,p):
                    d = distance_of_points(own_pos,p)
                    if d < lowest_distance:
                        lowest_distance=d
                        lowest_distance_index = i
                else:
                    p = None
            elif direction in ('left'):
                if p[0] < own_pos[0] and point_is_in_direction_from_point(own_pos,direction,p):
                    d = distance_of_points(own_pos,p)
                    if d < lowest_distance:
                        lowest_distance=d
                        lowest_distance_index = i
                else:
                    p = None
            elif direction in ('up'):
                if p[1] < own_pos[1] and point_is_in_direction_from_point(own_pos,direction,p):
                    d = distance_of_points(own_pos,p)
                    if d < lowest_distance:
                        lowest_distance=d
                        lowest_distance_index = i
                else:
                    p = None
        else:
            p = None
    return lowest_distance_index
