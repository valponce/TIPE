##Algorithme glouton
from pylab import *

def Voyageur_commerce (A): #S= liste ville, A= tableau (lignes villee de départ, colonne ville d'arrivéé)
    Chemin=[0]
    L=0                         # L= Longueur du parcours
    PasVus=list(range(1,len(A[0])))
    while PasVus!=[]:
        i=Chemin[-1] #position actuelle
        v=PasVus[0] #selection 1er ville non vue
        lm=A[i,v]  #longueur arrête

        #recherche ville plus proche non vue
        for j in PasVus[1:]:
            if A[i,j]<lm:
                lm=A[i,j]
                v=j
        L=L+lm  # nouvelle longueur totale
        Chemin.append(v)
        PasVus.remove(v)
    return (Chemin,L)

def liste_aleatoire (N):
    L=[]
    for i in range (N):
        L.append([uniform(0,100),uniform(0,100)])
    return L
                       
#print(liste_aleatoire (4))


def poids(a,b):
    return sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

#print(poids([2,1],[5,5]))

def ensemble_route (S):
    A=zeros((len(S),len(S)))
    for i in range (len(S)):
        for j in range (len(S)):
            A[i,j]=poids(S[i],S[j])
    return A
#print(ensemble_route (liste_aleatoire(4)))


def affiche(S, Chemin):
    figure()
    lx=[S[k][0] for k in Chemin]
    ly=[S[k][1] for k in Chemin]
    plot(lx,ly,color='black',marker='s')
    plot(S[0][0],S[0][1],color='blue',marker='o')
    show ( )

#S=liste_aleatoire(40)
#A=ensemble_route (S)
#Chemin,L=Voyageur_commerce(A)
#affiche(S, Chemin)

##S=[(1,2),(3,6),(5,4),(2,4),(3,2),(3,8),(9,7),(7,2),(0,5),(20,12)]
##A=ensemble_route (S)
##Chemin,L=Voyageur_commerce(A)
##print(L)
##affiche(S, Chemin)


#Probleme standard au format tsplib
import tsplib95
#problem = tsplib95.load('ch130.tsp')
problem = tsplib95.load('d2103.tsp')
S = [problem.node_coords[n] for n in problem.get_nodes()]
A = ensemble_route(S)
ch, l = Voyageur_commerce(A)
#affiche(S, ch)
from time import*

LN=[k for k in range (1,400,10)]
LT=[]
for k in LN:
    Abis=ensemble_route (S[:k])
    t0=perf_counter()
    Voyageur_commerce(Abis)
    t1=perf_counter()
    LT.append(t1-t0)

figure()
grid()
semilogy()
plot(LN,LT)
title('Temps d execution en fonction du nombre de villes')
plt.ylabel('log(t)')
plt.xlabel('Nombre de villes')
show()
              
