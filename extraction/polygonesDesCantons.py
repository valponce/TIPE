import geojson
import pickle
from shapely.geometry import shape
from canton import Canton

# chargement des donnees des cantons au format json
data = geojson.loads(open('swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.geojson', 'rb').read())

cantons = {}

n = 0
for feat in data['features']:
    # recuperation du nom du canton
    nom = feat["properties"]["NAME"]
    print (nom)
    # creation du canton s'il n'existe pas encore
    if nom not in cantons:
        canton = Canton(nom, n)
        cantons[nom] = canton
        n += 1
    # recuperation du canton
    canton = cantons[nom]
    # recuperation des coordonnees du polygone et ajout au canton
    coordonnees = feat["geometry"]["coordinates"]
    for string in coordonnees:
        canton.addPoly(shape(feat['geometry']))

# sauvegarde des cantons pour les differents cantons
pickle.dump(cantons, open("PolygonesCantons.pkl", 'wb'))
