import osmnx
import pickle
import sys, os
import networkx
import matplotlib.pyplot as plt

# recuperation du graphe de suisse simplifie et de la table de convertion
grapheSimple = pickle.load(open('SuisseSimplifiee.pkl', 'rb'))
tableConvertion = pickle.load(open('TableConvertion.pkl', 'rb'))

# calcul de tous les temps de parcours entre 2 noeuds
distances = dict(networkx.shortest_path_length(grapheSimple, weight='weight', ))
mesDistances = {tableConvertion[n1]:{tableConvertion[n2]:distances[n1][n2] for n2 in distances[n1]} for n1 in distances}

# sauvegarde
pickle.dump(mesDistances, open('SuisseDistances.pkl', 'wb'))

