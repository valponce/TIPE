import numpy as np
from pylab import figure,plot,show
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.colors
import pickle
import networkx

# recuperation du graphe complet de suisse
g = pickle.load(open("SuisseDiGraph.pkl", 'rb'))

# recuperations des coordonnees des points du graphe
coords, _, _, _ = pickle.load(open("SuisseTables.pkl", 'rb'))

# recuperation, et inversion de la table de convertion
tableConvertion = pickle.load(open('TableConvertion.pkl', 'rb'))
invTableConvertion = {v: k for k, v in tableConvertion.items()}


def tracer_polygone(ax,poly, **kwargs):
    '''
    Dessine a polygone sur le subplot ax
    A noter que les polygones sont des objets de la bibliotheque shapely,
    c'est a dire qu'ils peuvent contenir des trous. Ils sont definis
    comme un polygone principal "exterior" et une liste de polygones
    definissant d'eventuels trous "interiors"
    '''
    # creation du "path" comme compound avec l'exterieur comme premiere
    # composante et les "trous" commes autres composantes
    chemin = Path.make_compound_path(
        Path(np.asarray(poly.exterior.coords)[:, :2]),
        *[Path(np.asarray(contour.coords)[:, :2]) for contour in poly.interiors])
    etiquette = PathPatch(chemin, **kwargs)
    collection = PatchCollection([etiquette], **kwargs)
    ax.add_collection(collection, autolim=True)


def trace_solution(nom_de_fichier, couleur):
    # recuperation de la solution trouvee
    with open(nom_de_fichier, 'rb') as file:
        meilleur_longueur, chemin, listeVilles = pickle.load(file)
    # trace les villes sur le chemin
    for k in chemin:
        # k = k-ième ville du chemin
        # k[0] = numéro canton
        # k[1] = numéro de la ville dans le canton
        plot(listeVilles[k[0]][k[1]][0],listeVilles[k[0]][k[1]][1],
             color=couleurs[k[0]%len(couleurs)],marker='o')
    # calcul de la solution detaillee
    cheminDetaille = [invTableConvertion[chemin[0]]]
    for k in range(len(chemin)-1):
        a = invTableConvertion[chemin[k]]
        b = invTableConvertion[chemin[k+1]]
        cheminDetaille.extend(networkx.shortest_path(g, a, b, weight='duration')[1:])
    # dessin de la solution detaillee
    lx=[coords[k][0] for k in cheminDetaille]
    ly=[coords[k][1] for k in cheminDetaille]
    plot(lx,ly,color=couleur)


def plus_clair(hex_couleur, perc=0.7):
    """ prendre une couleur comme #87c95f et produire une variante plus claire ou plus foncée """
    rgb_hex = [int(hex_couleur[x:x+2], 16) for x in [1, 3, 5]]
    new_rgb_int = [c + int(perc*(255-c)) for c in rgb_hex]
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])


# recuperation d'un jeu de couleurs
couleurs = [matplotlib.colors.to_hex(plt.cm.tab20(i)) for i in range(20)]

# preparation de la figure
fig, ax = plt.subplots()
ax.set_xlim(260000,620000)
ax.set_ylim(5050000,5300000)
ax.axis('off')

# recuperation de la carte des cantons
with open("PolygonesCantons.pkl", 'rb') as file:
    polys = list(pickle.load(file).values())

# dessin des differents cantons, chacun avec une couleur claire differente
for n in range(len(polys)):
    couleur = couleurs[n%len(couleurs)]
    couleurClaire = plus_clair(couleur)
    for poly in polys[n].polygones:
        tracer_polygone(ax,poly, color=couleurClaire)

# recupere et dessine les solutions
trace_solution("solution.pkl", "black")

# dessin des meilleurs parcours 2023 #
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

#dessineParcours(utm2069, color='white')
dessineParcours(utm2101, color='grey')

plt.show()
