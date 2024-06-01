import osmnx
import pickle
import sys, os
import networkx

graphe = pickle.load(open('SuisseAvecDurees.pkl', 'rb'))

# projection de la carte pour pouvoir calculer des distances
projGraphe = osmnx.project_graph(graphe)

# consolidations des intersections, suppression des impasses
osmGraphe = osmnx.consolidate_intersections(projGraphe, rebuild_graph=True, tolerance=25, dead_ends=False)

# sauvegarde du graphe simplifie
pickle.dump(osmGraphe, open('SuisseConsolide.pkl', 'wb'))
