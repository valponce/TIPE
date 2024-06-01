import numpy as np,random,operator, matplotlib.pyplot as plt, matplotlib
from pylab import zeros,figure,plot,show
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.colors
from convert_data import convert

def obtenir_distance(route,td):
        '''calcul longueur route entre plusieurs points'''
        distance =0
        for i in range(0, len(route)-1):
            depart =route[i]
            arrivee =route[i + 1]
            distance+= td[depart][arrivee]
        return distance


def creationRoute(listeVilles):
    '''creation route entre toutes villes au hazard'''
    route=[]
    obligatoires=[]
    for x in range(len(listeVilles)):
        if len(listeVilles[x])>4:
            '''canton normal'''
            route.append((x,random.randint(0,len(listeVilles[x])-1))) 
        else:
            '''canton avec passages obligatoires où les seules villes sont ces passages
                sauf Bern qui sera rajoutée à la fin à la main'''
            obligatoires.append((x,k) for k in listeVilles[x] and (x,k)!=Bern)
    '''supression de deux villes au hasard car on a le droit de sauter deux cantons'''
    route=random.sample(route,len(route))[:-2]
    route.extend(obligatoires)
    return random.sample(route,len(route))+[bern]


def Tri_Parcours(population,td):
    ''' tri Polulation en fonction de la longueur totale de chaque route, population =liste de routes'''
    M=[]
    for i in range (0,len(population)):
        M.append((i,obtenir_distance(population[i],td)))
    return sorted(M,key = lambda item: item[1]) #lambda =fonction (entrée= item et renvoie item[1]) #sorted =tri par distance

def selection (parcours_trie,nbElite):
    '''selection nbElite première puis autre en fonction pourcentage'''
    selectionResultats=[]
    cum_som=0
    tot_som=sum([item[1] for item in parcours_trie])
    for i in range(0, nbElite):
        selectionResultats.append(population[parcours_trie[i][0]]) # recupération route i
        cum_som+=parcours_trie[i][1] #ajout longueur route i
    for i in range(nbElite, len(parcours_trie)):
        seuil = random.random()
        #selection pourcentage et comparaison au pourcentage sur somme distance pour savoir si on garde ville
        cum_som+=parcours_trie[i][1]
        #print(i,seuil,cum_som/tot_som)
        if seuil >= cum_som/tot_som:
            selectionResultats.append(population[parcours_trie[i][0]])
    return selectionResultats


def croiser(parent1, parent2):
    '''combinaison de route avec 2 particuliers'''
    fils = []
    filsP1 = []
    filsP2 = []

    '''selection d'une partie du parent1 excluant la ville d'arrivée qui doit être Bern'''
    geneA = int(random.random() * (len(parent1)-1))
    geneB = int(random.random() * (len(parent1)-1))
    while geneA==geneB:
        geneB = int(random.random() * len(parent1))
    #print('gene',geneA,geneB)
    debutGene = min(geneA, geneB)
    finGene = max(geneA, geneB)
    for i in range(debutGene, finGene):
        filsP1.append(parent1[i])

    '''on conserve ensuite de parent2 :
        - les villes de cluster non visités dans fils1
        - les villes obligatoires non visités dans fils1 '''
    clusterfilsP1=[k[0] for k in filsP1]
    filsP2 = [item for item in parent2
              if item[0] not in clusterfilsP1
              or (item in villesObligatoires and item not in filsP1) ]
    fils = filsP1 + filsP2
    
    ''' l'algorithme précédent peut amener à visiter plus de cluster que nécessaire :
        chaque parent ne visite que 24 des 26 cantons, mais s'ils n'évitent pas les mêmes cantons,
        le fils peut visiter jusqu'à 26 cantons.
        Nous allons donc en suppimer 2 au hasard.'''
    clusterfils = set([k[0] for k in fils])
    while len(clusterfils) > 25: # 24 + 1 pour les inclusions étrangères qui ont -1 pour numéro de canton
        n = int(random.random() * (len(fils)))
        ville = fils[n]
        if ville not in villesObligatoires:
            clusterfils.remove(ville[0])
            fils.remove(ville)
    return fils


def croiserPopulation(popAccouplement, nbElite,nbEnfants):
    ''' combinaison de route sur population entière
        popAccouplement supposé ordonné'''
    listeEnfants = []
    longueur = nbEnfants- nbElite
    l=len(popAccouplement)
    groupe = random.sample(popAccouplement,l)

    for i in range(0,nbElite):
        listeEnfants.append(popAccouplement[i])
    '''création nouveau enfant'''
    for i in range(0, longueur):
        enfant = croiser(groupe[i%l], groupe[(l-i-1)%l])
        #print('croissement',groupe[i],groupe[len(popAccouplement)-i-1],enfant)
        listeEnfants.append(enfant)
    return listeEnfants

def muter(route, tauxMutation, tauxMutationCluster,listeVilles,td):
    for echange in range(len(route)-1): # on laisse Bern en fin de route
        ville1 = route[echange]
        '''inversion de deux villes dans la route '''
        if(random.random() < tauxMutation):
            echangeAvec = int(random.random() * (len(route)-1)) # on évite Bern
            #print('muter',echange,echangeAvec)
            ville2 = route[echangeAvec]
            
            route[echange] = ville2
            route[echangeAvec] = ville1

        ''' changement de ville dans le cluster'''
        if (random.random () < tauxMutationCluster) and ville1 not in villesObligatoires :
            echangeAvec2 = int(random.random() * len(listeVilles[ville1[0]])) #ville1[0]= numéro canton, ville1= n-ième ville de la route
            route[echange]= (ville1[0],echangeAvec2)

        ''' optimisation 2op pour optimiser la convergence de l'algo'''
        for autre in range(echange+2, min(echange+4, len(route)-2)): # on évite Bern 
            i1= route[echange]
            i2= route[echange+1]
            j1= route[autre]
            j2= route[autre+1]
            gain= td[i1][i2]+td[j1][j2]-td[i1][j1]-td[i2][j2]
            if gain >0 :
                r=route[echange+1]
                route[echange+1]= route[autre]
                route[autre]=r
    return route


def muterPopulation(population, tauxMutation, tauxMutationCluster,listeVilles,td):
    popMutee = []
    for route in range(0, len(population)):
        IndMutee = muter(population[route], tauxMutation,tauxMutationCluster,listeVilles,td)
        popMutee.append(IndMutee)
    return popMutee

import pickle

with open("ListeVilles.pkl", 'rb') as file:
    ListeVilles = pickle.load(file)

with open("Citydistances.pkl", 'rb') as file:
    td = pickle.load(file)

with open("CantonPolys.pkl", 'rb') as file:
    polys = list(pickle.load(file).values())

with open("VillesProtegees.pkl", 'rb') as file:
    bern, villesObligatoires = pickle.load(file)


print("data loaded")   
lpop=400
nbElite=100
n=2000

population=[creationRoute(ListeVilles) for i in range(lpop)]
gagnant=None
meilleur_longueur=9999999999999

for i in range (n):
    parcours_trie=Tri_Parcours(population,td)
    if parcours_trie[0][1]<meilleur_longueur:
        meilleur_longueur=parcours_trie[0][1]
        gagnant= population[parcours_trie[0][0]]
    popAccouplement=selection(parcours_trie,nbElite)
    nouvelle_pop=croiserPopulation(popAccouplement, nbElite,lpop)
    population=muterPopulation (nouvelle_pop,0.005,0.01,ListeVilles,td)
parcours_trie=Tri_Parcours(population,td)    

couleurs = [matplotlib.colors.to_hex(plt.cm.tab20(i)) for i in range(20)]

def tracer_polygone(ax,poly, **kwargs):
    chemin = Path.make_compound_path(Path(np.asarray(poly.exterior.coords)[:, :2]),*[Path(np.asarray(contour.coords)[:, :2]) for contour in poly.interiors])
    etiquette = PathPatch(chemin, **kwargs)
    collection = PatchCollection([etiquette], **kwargs)    
    ax.add_collection(collection, autolim=True)

def plus_clair(hex_couleur, perc=0.7):
    """ prendre une couleur comme #87c95f et produire une variante plus claire ou plus foncée """
    rgb_hex = [int(hex_couleur[x:x+2], 16) for x in [1, 3, 5]]
    new_rgb_int = [c + int(perc*(255-c)) for c in rgb_hex]
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])

def affiche(Chemin,listeVilles):
    fig, ax = plt.subplots()
    ax.set_xlim(260000,620000)
    ax.set_ylim(5050000,5300000)
    ax.axis('off')
    lx=[listeVilles[k[0]][k[1]][0] for k in Chemin] # k=k-ième ville du chemin ,k[0]=numéro canton,k[1]= numéro de la ville dans le canton
    ly=[listeVilles[k[0]][k[1]][1] for k in Chemin]
    plot(lx,ly,color='black')
    #plot(listeVilles[Chemin[0][0]][Chemin[0][1]][0],listeVilles[Chemin[0][0]][Chemin[0][1]][1],color='blue',marker='o')
    for k in Chemin:
        plot(listeVilles[k[0]][k[1]][0],listeVilles[k[0]][k[1]][1],color=couleurs[k[0]%len(couleurs)],marker='o')
    for n in range(len(listeVilles)):
        couleur = couleurs[n%len(couleurs)]
        # draw cantons
        couleurClaire = plus_clair(couleur)
        for poly in polys[n].polys:
            tracer_polygone(ax,poly, color=couleurClaire)
    show ( )

print(meilleur_longueur)
print(gagnant)
pickle.dump((meilleur_longueur,gagnant,ListeVilles),open('solution.pkl','wb'))
affiche(gagnant,ListeVilles)

