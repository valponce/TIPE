import osmnx
import pickle

# buffer_dist permet de prendre un peu de marge pour couvrir les inclusions allemande,
# suisse et francaises presentes en suisse
# On telecharge de reseau pour les cyclistes
# Attention, il faut une machine avec beaucoup de memoire (75 Go)
# et cela prend plus ou moins 1h
graphe = osmnx.graph_from_place("Switzerland", simplify=True, network_type="bike", buffer_dist=2000)

pickle.dump(graphe, open('Suisse.pkl', 'wb'))

