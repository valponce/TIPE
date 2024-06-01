import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.colors
import pickle
import networkx

def dessinePolygone(ax, polygone, **kwargs):
    '''
    Dessine a polygone sur le subplot ax
    A noter que les polygones sont des objets de la bibliotheque shapely,
    c'est a dire qu'ils peuvent contenir des trous. Ils sont definis
    comme un polygone principal "exterior" et une liste de polygones
    definissant d'eventuels trous "interiors"
    '''
    # creation du "path" comme compound avec l'exterieur comme premiere
    # composante et les "trous" commes autres composantes
    path = Path.make_compound_path(
        Path(np.asarray(polygone.exterior.coords)[:, :2]),
        *[Path(np.asarray(trou.coords)[:, :2]) for trou in polygone.interiors])
    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)
    ax.add_collection(collection, autolim=True)

    
def eclaircir(hex_color, pourcentage=0.7):
    """
    convertit une couleur au format hexadecimal (comme #87c95f) en une
    couleur plus claire selon le pourcentage donne
    """
    rgb_hex = [int(hex_color[x:x+2], 16) for x in [1, 3, 5]]
    new_rgb_int = [c + int(pourcentage*(255-c)) for c in rgb_hex]
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])

######################
# dessin des cantons #
######################

# recuperation d'un jeu de couleurs
couleurs = [matplotlib.colors.to_hex(plt.cm.tab20(i)) for i in range(20)]

# preparation de la figure
fig, ax = plt.subplots()

# recuperation ds donnees geometriques des cantons
polygonesCantons = list(pickle.load(open("PolygonesCantons.pkl", 'rb')).values())

# dessin des differents cantons, chacun avec une couleur claire differente
for n in range(len(polygonesCantons)):
    couleur = couleurs[n%len(couleurs)]
    couleurClaire = eclaircir(couleur)
    for polygone in polygonesCantons[n].polygones:
        dessinePolygone(ax, polygone, color=couleurClaire)

###############################################
# dessin des points de passage de la solution #
###############################################
        
# recuperation de la solution trouvee
meilleurChemin = pickle.load(open('solution.pkl', 'rb'))

# recuperation des tables de correspondance simplifiees
coordonneesSimples, _, cantonPourNoeudsSimple = pickle.load(open("SuisseTablesSimplifiees.pkl", 'rb'))
    
# recuperation du graphe simplifie
grapheSimple = pickle.load(open("SuisseSimplifiee.pkl", 'rb'))

# dessin des points de passage dans chaque canton
for noeud in meilleurChemin:
    couleur = couleurs[cantonPourNoeudsSimple[noeud]%len(couleurs)]
    networkx.draw_networkx_nodes(grapheSimple, coordonneesSimples, [noeud], node_size=60, node_color=couleur)
    
#############################################
# dessin des points de la solution complete #
#############################################

# recuperation du graphe complet de suisse
g = pickle.load(open("SuisseDiGraph.pkl", 'rb'))

# recuperations des tables de correspondance. Seules les coordonnees des points nous interessent
coords, _, _, _ = pickle.load(open("SuisseTables.pkl", 'rb'))

# recuperation de la solution detaillee
route = pickle.load(open("solutionDetaillee.pkl", 'rb'))

# dessin de la solution detaillee
pairRoute = list(networkx.utils.pairwise(route))
networkx.draw_networkx_edges(g, coords, pairRoute, node_size=0, width=2, arrows=False)

######################################
# dessin des meilleurs parcours 2023 #
######################################

import geopandas as gpd

coordonnees2069 = eval(open('2069.txt','r').read()) # vainqueur
coordonnees2101 = eval(open('2101.txt','r').read()) # 2eme

# conversion vers system UTM
utm="+proj=utm +zone=32 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
wgs84="EPSG:4326"

def conversion(coordonnees):
    '''
    convertit une suite de points donnes via longitude, latitude
    en system UTM
    '''
    xs = [a for a,b in coordonnees]
    ys = [b for a,b in coordonnees]
    geometry = gpd.points_from_xy(xs, ys, crs=wgs84)
    geo = geometry.to_crs(utm)
    return geo

utm2069 = conversion(coordonnees2069)
utm2101 = conversion(coordonnees2101)

# dessin des parcours
def dessineParcours(utm, **kwargs):
    '''
    dessine un parcours donnees en coordonnees utm
    '''
    xs = [point.x for point in utm]
    ys = [point.y for point in utm]
    plt.plot(xs, ys, **kwargs)

dessineParcours(utm2069, color='white')
dessineParcours(utm2101, color='grey')

plt.show()
