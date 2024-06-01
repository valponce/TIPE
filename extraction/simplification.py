import pickle

def noeudInterne(graphe, noeud, cantonPourNoeud):
    '''
    verifie si un noeud est a l'interieur d'un canton, c'est a dire si
    tous ses voisins sont dane le meme canton
    '''
    canton = cantonPourNoeud[noeud]
    for p, _ in graphe.in_edges(noeud):
        if cantonPourNoeud[p] != canton:
            return False
    for _, p in graphe.out_edges(noeud):
        if cantonPourNoeud[p] != canton:
            return False
    return True


def simplifierGraphe(graphe, cantonPourNoeud, cantonASupprimer, noeudsProteges, maxCon=None):
    '''
    supprime les noeuds internes a un canton en ne gardant que ceux "sur le bord",
    c'est a dire connectes a au moins un noeud en dehors du canton.
    Recalcule les connections et les poids (temps de parcours) de celles-ci
    L'algorithme est le suivant :
      - on passe tous les noeud en revue
      - si un noeud A est interne au canton, on le supprime
      - on reconnecte alors tous les noeuds I qui menaient a A a tous les noeuds O
        qui en provenaient avec comme poids poids de IA + poids de AO
      - s'il y a plusieurs possibilites pour aller de I a O, on garde le poids minimal,
        c'est a dire le chemin le plus rapide
    Pour accelerer l'agorithme et ne pas faire exploser le nouveau graphe a mi parcours,
    on va se limiter a simplifier les noeuds avec "peu" de connections,
    a savoir moins de maxCon. Les autres ne sont pas touches
    On va egalement supprimer sans condition tous les noeuds d'un certain nombre de cantons,
    en pratique ceux ou il y a un point de passage obligatoire.
    Enfin on ne touche pas aux noeuds proteges, c'est a dire aux points de passage
    obligatoires du challenge)
    '''
    # on cree un replique du graphe initial sur lequel on v supprimer les noeuds
    grapheSimple = graphe.copy()
    # on passe en revue les noeuds du graphe initial
    for noeud in graphe.nodes:
        if noeud in noeudsProteges: continue
        if cantonPourNoeud[noeud] in cantonASupprimer or noeudInterne(grapheSimple, noeud, cantonPourNoeud):
            # on peut supprimer le noeud
            aretesEntrantes = list(grapheSimple.in_edges(noeud))
            aretesSortantes = list(grapheSimple.out_edges(noeud))
            # si trop de connections, on abandonne
            if maxCon and (len(set(aretesEntrantes + aretesSortantes)) > maxCon): continue
            # on passe en revue toutes les paires areteEntrante - areteSortante
            for entree, _ in aretesEntrantes:
                for _, sortie in aretesSortantes:
                    # suppression des boucles
                    if entree == sortie: continue
                    # calcul du nouveau temps de parcours entree-sortie
                    tempsParcours = grapheSimple[entree][noeud]['weight'] + grapheSimple[noeud][sortie]['weight']
                    # creation de la nouvelle connection ou mise a jour de son temps de parcours
                    # si elle existait deja
                    if sortie in grapheSimple[entree]:
                        # mise a jour
                        grapheSimple[entree][sortie]['weight'] = min(tempsParcours, grapheSimple[entree][sortie]['weight'])
                    else:
                        # nouvelle connection
                        grapheSimple.add_edge(entree, sortie, weight=tempsParcours)
            # maintenant qu'on a recree toutes les connections, on supprime le noeud
            grapheSimple.remove_node(noeud)
    return grapheSimple


# recuperation du digraph et des tables de correspondance
graphe = pickle.load(open('SuisseDiGraph.pkl', 'rb'))
coordonnees, noeudsDunCanton, cantonPourNoeud, noeudPourOsmid = pickle.load(open('SuisseTables.pkl', 'rb'))

pointsDePassage = {'Campione d\'Italia': 9008012407, 'Busingen': 390407244,
                   'alte Rheinbrücke': 1378764555, 'Pont de Grilly': 1186596358,
                   'Rheinbrücke': 176724546, 'BERN': 33202504}
osmids = pointsDePassage.values()

# simplification du graphe
# initialement, la simplification se faisait en une seule passe, mais le nombre total
# de connection du graphe explosait a mi-parcours rendant l'algorithm extremement lent
# et tres gourmant en memoire.
# L'astuce pour le rendre faisable a ete de ne traiter dans un premier temps que les noeuds
# a faible nombre de connections pour reduite le nombre de noeuds sans faire trop exploser
# les connections, puis faire un 2eme passe en augmentant la limite et ainsi de suite
noeudsProteges = [noeudPourOsmid[id] for id in osmids]
cantonASupprimer = [cantonPourNoeud[noeudPourOsmid[a]] for a in osmids]
grapheSimple = simplifierGraphe(graphe, cantonPourNoeud, cantonASupprimer, noeudsProteges, 20)
print(grapheSimple)
grapheSimple = simplifierGraphe(grapheSimple, cantonPourNoeud, cantonASupprimer, noeudsProteges, 50)
print(grapheSimple)
grapheSimple = simplifierGraphe(grapheSimple, cantonPourNoeud, cantonASupprimer, noeudsProteges, 100)
print(grapheSimple)
grapheSimple = simplifierGraphe(grapheSimple, cantonPourNoeud, cantonASupprimer, noeudsProteges, 200)
print(grapheSimple)
grapheSimple = simplifierGraphe(grapheSimple, cantonPourNoeud, cantonASupprimer, noeudsProteges, 400)
print(grapheSimple)
grapheSimple = simplifierGraphe(grapheSimple, cantonPourNoeud, cantonASupprimer, noeudsProteges, 600)
print(grapheSimple)
grapheSimple = simplifierGraphe(grapheSimple, cantonPourNoeud, cantonASupprimer, noeudsProteges, 800)
print(grapheSimple)
grapheSimple = simplifierGraphe(grapheSimple, cantonPourNoeud, cantonASupprimer, noeudsProteges, None)
print(grapheSimple)

# calcul de la nouvelle liste de villes par canton
listeVilles=[]
tableConversion={}
villesProtegees=[]
for c in noeudsDunCanton:
    listeCoord=[]
    ncluster=len(listeVilles)
    for n in c:
        if n in grapheSimple.nodes():
            tableConversion[n]=(ncluster,len(listeCoord))
            listeCoord.append(coordonnees[n])
            if n in noeudsProteges:
                villesProtegees.append(tableConvertion[n])
    listeVilles.append(listeCoord)
    
bern=tableConversion[pointsDePassage['BERN']]

pickle.dump((bern,villesProtegees), open('VillesProtegees', 'wb'))    
pickle.dump(tableConversion, open('TableConversion.pkl', 'wb'))
pickle.dump(grapheSimple, open('SuisseSimplifiee.pkl', 'wb'))
pickle.dump(listeVilles, open('ListeVilles.pkl', 'wb'))
