import numpy as np,random,operator, matplotlib.pyplot as plt
from pylab import zeros,figure,plot,show


def TableauDistance (Citylist):
    '''prend une liste de villes (= couple de coordonnées) et renvoie tableau des distances entre chaque'''
    td={}
    for clusteri in range (len(Citylist)):
        for i in range (len(Citylist[clusteri])):
            td[(clusteri,i)]={}
            x,y=Citylist[clusteri][i]
            for clusterj in range (len(Citylist)):
                for j in range (len(Citylist[clusterj])):
                    xbis,ybis= Citylist[clusterj][j]
                    distance=np.sqrt((abs(x-xbis) ** 2) + (abs(y-ybis) ** 2))
                    td[(clusteri,i)][(clusterj,j)]=distance
    return td

#Citylist=[(1,2),(3,6),(5,4),(2,4),(3,2),(3,8),(9,7),(7,2),(0,5),(20,12)]
#print(TableauDistance (Citylist))


def get_distance(route,td):
        '''calcul longueur route entre plusieurs points'''
        distance =0
        for i in range(0, len(route)-1):
            fromCity =route[i]
            toCity =route[i + 1]
            distance+= td[fromCity][toCity]
        return distance



def createRoute(cityList):
    '''creation route entre toutes villes au hazard'''
    route=[]
    liste_canton = random.sample(range(len(cityList)),len(cityList))
    for x in liste_canton:
        route.append((x,random.randint(0,len(cityList[x])-1)))
    return route

#L=[[1,2,3],[4,5,6],[7,6]]
#print(createRoute (L))

def Tri_Parcours(population,td):
    ''' tri Polulation en fonction de la longueur totale de chaque route, population =liste de routes'''
    M=[]
    for i in range (0,len(population)):
        M.append((i,get_distance(population[i],td)))
    return sorted(M,key = lambda item: item[1]) #lambda =fonction (entrée= item et renvoie item[1]) #sorted =tri par Fitness

def selection (parcours_trie,eliteSize):
    '''selection elitesize première puis autre en fonction pourcentage'''
    selectionResults=[]
    cum_som=0
    tot_som=sum([item[1] for item in parcours_trie])
    for i in range(0, eliteSize):
        selectionResults.append(population[parcours_trie[i][0]]) # recupération route i
        cum_som+=parcours_trie[i][1] #ajout longueur route i
    for i in range(eliteSize, len(parcours_trie)):
        pick = random.random()
        #selection pourcentage et comparaison au pourcentage sur somme distance pour savoir si on garde ville
        cum_som+=parcours_trie[i][1]
        #print(i,pick,cum_som/tot_som)
        if pick >= cum_som/tot_som:
            selectionResults.append(population[parcours_trie[i][0]])
    return selectionResults


def breed(parent1, parent2):
    '''combinaison de route avec 2 particuliers'''
    fils = []
    filsP1 = []
    filsP2 = []
    
    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))
    while geneA==geneB:
        geneB = int(random.random() * len(parent1))
    #print('gene',geneA,geneB)
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        filsP1.append(parent1[i])
    clusterfilsP1=[k[0] for k in filsP1]
    filsP2 = [item for item in parent2 if item[0] not in clusterfilsP1]

    fils = filsP1 + filsP2
    return fils

def breedPopulation(matingpool, eliteSize,nbchildren):
    ''' combinaison de route sur population entière
        matingpool supposé ordonné'''
    children = []
    length = nbchildren- eliteSize
    l=len(matingpool)
    pool = random.sample(matingpool,l)

    for i in range(0,eliteSize):
        children.append(matingpool[i])
    #création nouveau child
    for i in range(0, length):
        child = breed(pool[i%l], pool[(l-i-1)%l])
        #print('breeding',pool[i],pool[len(matingpool)-i-1],child)
        children.append(child)
    return children

def mutate(route, mutationRate, mutationRateCluster,citylist,td):
    '''échange de villes dans la route'''
    for swapped in range(len(route)):
        city1 = route[swapped]
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(route))
            #print('mutate',swapped,swapWith)
            city2 = route[swapWith]
            
            route[swapped] = city2
            route[swapWith] = city1
        if (random.random () < mutationRateCluster):
            swapWith2 = int(random.random() * len(citylist[city1[0]])) #city1[0]= numéro canton, city1= n-ième ville de la route
            route[swapped]= (city1[0],swapWith2)
        for other in range(swapped+2, min(swapped+4, len(route)-1)): #2op
            i1= route[swapped]
            i2= route[swapped+1]
            j1= route[other]
            j2= route[other+1]
            gain= td[i1][i2]+td[j1][j2]-td[i1][j1]-td[i2][j2]
            if gain >0 :
                r=route[swapped+1]
                route[swapped+1]= route[other]
                route[other]=r
    return route


def mutatePopulation(population, mutationRate, mutationRateCluster,citylist,td):
    mutatedPop = []
    for route in range(0, len(population)):
        mutatedInd = mutate(population[route], mutationRate,mutationRateCluster,citylist,td)
        mutatedPop.append(mutatedInd)
    return mutatedPop

import pickle

with open("Citylist.pkl", 'rb') as file:
    Citylist = pickle.load(file)
with open("D:\TIPE\Citydistances.pkl", 'rb') as file:
    td = pickle.load(file)

print("data loaded")   
lpop=200
eliteSize=50
n=50

population=[createRoute(Citylist) for i in range(lpop)]
winner=None
best_length=9999999999999

for i in range (n):
    parcours_trie=Tri_Parcours(population,td)
    if parcours_trie[0][1]<best_length:
        best_length=parcours_trie[0][1]
        winner= population[parcours_trie[0][0]]
    matingpool=selection(parcours_trie,eliteSize)
    new_pop=breedPopulation(matingpool, eliteSize,lpop)
    population=mutatePopulation (new_pop,0.005,0.01,Citylist,td)
parcours_trie=Tri_Parcours(population,td)    


def affiche(Chemin,Citylist):
    figure()
    lx=[Citylist[k[0]][k[1]][0] for k in Chemin] # k=k-ième ville du chemin ,k[0]=numéro canton,k[1]= numéro de la ville dans le canton
    ly=[Citylist[k[0]][k[1]][1] for k in Chemin]
    plot(lx,ly,color='black',marker='s')
    plot(Citylist[Chemin[0][0]][Chemin[0][1]][0],Citylist[Chemin[0][0]][Chemin[0][1]][1],color='blue',marker='o')
    show ( )

print(best_length)
print(winner)
affiche(winner,Citylist)

