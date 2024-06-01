import pickle
import sys, os
import networkx

# recuperation du graphe consolide
grapheConsolide = pickle.load(open('SuisseConsolide.pkl', 'rb'))

# conversion du graphe consolide de type multidigraph en un digraph simple ou on supprime les
# boucles et ou on ne garde que le chemin le plus court entre 2 points donnes
# le nouveau graphe a la duree de parcours comme poids des aretes (parametre weight)
graphe = networkx.DiGraph()
for u,v,data in grapheConsolide.edges(data=True):
    if u == v: continue
    w = data['duree']
    if graphe.has_edge(u,v):
        if w < graphe[u][v]['weight']:
            graphe[u][v]['weight'] = w
    else:
        graphe.add_edge(u, v, weight=w)

        
# recuperation des polygones des differents cantons
cantons = pickle.load(open("PolygonesCantons.pkl", 'rb')).values()


def trouveCanton(point, cantonProbable):
    '''trouve le canton dans lequel se trouve un point.
       si cantonProbable n'est pas None, il sera teste en premier
       Cela permet d'optimiser la recherche
    '''
    # on essaye d'abord le canton probable s'il est donne
    if cantonProbable and cantonProbable.contient(point):
        return cantonProbable
    # sinon on essaye tous les cantons un par un
    for canton in cantons:
        if canton.contient(point):
            return canton
    # Si aucun canton ne contient le point, on retourne None
    return None


# creation de 3 tables de correspondances :
#  - coordonnees d'un noeud
#  - canton d'un noeud
#  - liste de noeud pour un canton
coordonnees = {}
cantonPourNoeud = {}
noeudsDunCanton = [[] for n in range(len(cantons))]
# dernier canton visite. Utilise comme canton probable lors des appels a trouveCanton
dernierCanton = None
for noeud in graphe._node:
    coords = (grapheConsolide._node[noeud]['x'], grapheConsolide._node[noeud]['y'])
    canton = trouveCanton(coords, dernierCanton)
    coordonnees[noeud] = coords
    if canton :
        noeudsDunCanton[canton.numero].append(noeud)
    cantonPourNoeud[noeud] = canton.numero if canton else -1
    if canton:
        dernierCanton = canton


# creation d'une derniere table de correspondance donnant les numeros
# de noeud pour les points de passage obligatoires en fonction de leur osmid
pointsDePassage = {'Campione d\'Italia': 9008012407, 'Busingen': 390407244, 'alte Rheinbrücke': 1378764555, 'Pont de Grilly': 1186596358, 'Rheinbrücke': 176724546, 'BERN': 33202504}
osmids = pointsDePassage.values()
noeudPourOsmid = {}
for n in grapheConsolide._node:
    l = grapheConsolide._node[n]['osmid_original']
    if isinstance(l, str):
        for ll in [int(c) for c in l[1:-1].split(',')]:
            for p in osmids:
                if p == ll:
                    noeudPourOsmid[p] = n
    else:
        for p in osmids:
            if p == l:
                noeudPourOsmid[p] = n


# sauvegarde du digraphe et des differentes tables de correspondance
pickle.dump(graphe, open('SuisseDiGraph.pkl', 'wb'))
pickle.dump((coordonnees, noeudsDunCanton, cantonPourNoeud, noeudPourOsmid), open('SuisseTables.pkl', 'wb'))

