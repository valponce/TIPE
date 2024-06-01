'''
On utilise le calcul tu temps de parcous a velo trouve sur
http://www.velomath.fr/dossier_velo_equation/velo_equation.html
Les parametres utilises sont Cx = 0.2, f = 1, poids = 72
Donc l'equation finale est de la forme puissance = 2*(1+pente)*vitesse+0.005*vitesse^3
'''

def puissanceDeVitesse(vitesse, pente):
  '''
  calcule la puissance necessaire pour atteindre une certaine vitess
  sur un certaine pente
  la vitesse est en km/h, la pente en %, le resultat en Watts
  '''
  return (2*(1+pente)+0.005*vitesse*vitesse)*vitesse

def vitessePourPuissance(puissance, pente):
  '''
  calcule la vitesse atteinte pour une puissance donnee sur une pente donnee
  la puissance est en Watts, la pente en %, le resultat en km/h
  '''
  # dichotomie
  vmin = 0
  vmax = 80
  pmin = puissanceDeVitesse(vmin, pente)
  pmax = puissanceDeVitesse(vmax, pente)
  while pmax - pmin > 1:
    vmoy = (vmin+vmax)/2
    pmoy = puissanceDeVitesse(vmoy, pente)
    if pmoy < puissance:
      pmin = pmoy
      vmin = vmoy
    else:
      pmax = pmoy
      vmax = vmoy
  return vmoy

# Table de valeurs precalculees de la vitesse pour une pente donnee
# on suppose la puissance constante a 250W
vitessePourPente = {}
for n in range(-30,31):
  pente = n/2
  vitessePourPente[pente] = vitessePourPuissance(250, pente)

def calculeVitesse(pente):
  '''
  Calcule la vitesse pour une pente donnee
  Pour les pentes superieures a 15%, on utilise 15%
  On fait une interpolation lineaire entre les points du tableau precalcule
  '''
  pente = max(-15, min(14.5, pente))
  penteMin = int(pente*2)/2
  penteMax = penteMin+0.5
  penteDelta = pente - penteMin
  delta = vitessePourPente[penteMax] - vitessePourPente[penteMin]
  return vitessePourPente[penteMin] + penteDelta*2*delta

def tempsDeParcours(distance, pente):
  '''
  Calcule le temps de parcours a velo pour une distance donnee avec une
  pente moyenne donnee
  le distance est en km, le temps de parcours en secondes
  '''
  return 3600 * distance / calculeVitesse(pente)

import requests

# table des altitudes deja calculees
altitudes = {}

serveurOpenElevation = 'http://0.0.0.0:8080/'
def calculeAltitude(point, noeud):
  '''
  Trouve l'altitude pour un point donnee
  Garde en memoire dans altitudes les valeurs deja trouvees
  Si la valeur n'est pas connue, interroge le serveur open-elevation
  Ici on utilise le serveur local qui tourne par defaut sur le port 8080
  '''
  if point not in altitudes:
    r = requests.get(serveurOpenElevation + 'api/v1/lookup?locations=%f,%f' %
                     (noeud['y'], noeud['x']),
                     headers={'Accept': 'application/json'})
    altitudes[point] = r.json()['results'][0]['elevation']
  return altitudes[point]

'''Table des facteurs de ralentissement pour des surfaces connues'''
tableDeRalentissement = {
    'paved' : 1,
    'asphalt' : 1,
    'chipseal' : 1.1,
    'concrete' : 1.1,
    'paving_stones': 1.5,
    'sett' : 1.3,
    'brick' : 1.2,
    'metal': 1.2,
    'wood' : 1.2,
    'compacted' : 2,
}

def sralentissementPourSurface(s):
  '''
  retourne une estimation du ralentissement pour une surface donnee
  Cette surface peut aussi etre une liste de surfaces, dans ce cas
  on prend la ralentissement maximum en compte
  '''
  if isinstance(s, list):
    r = 1
    for t in s:
      r = max(r, ralentissementPourSurface(t))
    return r
  if ':' in s : s = s[:s.find(':')]
  return tableDeRalentissement[s]

def ralentissement(data):
  '''
  estimation du ralentissement du au type de revetement
  1 = pas ralentissment
  2 = feux fois plus lent
  '''
  highway = data['highway']
  # si on a un "path" ou un "track", on cherche a utiliser sa surface
  if highway == 'path' or highway == 'track' or 'path' in highway or 'track' in highway:
    if 'surface' in data:
        s = data['surface']
        return ralentissementPourSurface(s)
    else:
      # si la surface est inconnue, on suppose qu'on a affaire a un chemin -> facteur 2
      return 2
  # si on a une voie de service, on suppose un ralentissement de 50%
  if highway == 'service' or 'service' in highway:
      return 1.5
  # dans les autres cas, pas de ralentissement
  return 1

import pickle
import networkx

graphe = pickle.load(open('Suisse.pkl', 'rb'))

for u,v,k,data in graphe.edges(keys=True, data=True):
  altitudeU = calculeAltitude(u, graphe._node[u])
  altitudeV = calculeAltitude(v, graphe._node[v])
  distance = data['length']
  pente = (altitudeV-altitudeU)/distance*100
  t = tempsDeParcours(distance/1000, pente)
  # prise en compte du type de revetement
  t = t * ralentissement(data)
  networkx.set_edge_attributes(graphe, {(u,v,k):{"duree":t}})

pickle.dump(graphe, open('SuisseAvecDurees.pkl', 'wb'))
