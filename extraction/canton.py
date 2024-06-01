import shapely.geometry
import osmnx

class Canton:
    '''
    Definition d'un canton comme une region de l'espace delimitee par
    un jeu de polygones avec 2 attributs : un nom et un numero.
    A noter que les polygones sont des objets de la bibliotheque shapely,
    c'est a dire qu'ils peuvent contenir des trous. Ils sont definis
    comme un polygone principal "exterior" et une liste de polygones
    definissant d'eventuels trous "interiors"
    '''

    def __init__(self, nom, n):
        self.nom = nom
        self.numero = n
        self.polygones = []

    def addPoly(self, polygone):
        '''
        ajoute un nouveau polygone au canton
        '''
        self.polygones.append(osmnx.projection.project_geometry(polygone)[0])

    def contient(self, coordonnees):
        '''
        permet de savoir si un point donne est a l'interieur
        du canton ou non
        '''
        point = shapely.geometry.Point(*coordonnees)
        for polygone in self.polygones:
            if polygone.contains(point): return True
        return False

