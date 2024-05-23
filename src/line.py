from typing import Callable, Literal, Any
def line(p1:tuple[int,int],p2:tuple[int,int])->list[tuple[int,int]]:
    x0 = p1[0]
    y0 = p1[1]
    x1 = p2[0]
    y1 = p2[1]
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    
    return points

def funcline(p1:tuple[int,int],p2:tuple[int,int],func:Callable[[int,int,Any],Literal[None]],args:list[Any]=[])->Literal[None]:
    points = line(p1,p2)
    for point in points:
        func(*point,*args)