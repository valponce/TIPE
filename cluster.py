import shapely.geometry
import osmnx

class Cluster:
    def __init__(self, name, n):
        self.name = name
        self.number = n
        self.polys = []
    def addPoly(self, shape):
        self.polys.append(osmnx.projection.project_geometry(shape)[0])
    def contains(self, coord):
        point = shapely.geometry.Point(*coord)
        for poly in self.polys:
            if poly.contains(point): return True
        return False

