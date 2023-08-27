import pickle

-with open("D:\TIPE\SwissSimpleGraph.pkl", 'rb') as file:
    graph, coords, clusters, nodeToclusters = pickle.load(file)

Citys=[[k for k in c] for c in clusters]
Citylist=[[coords[k] for k in c] for c in clusters]

with open("Citylist.pkl", 'wb') as file:
        pickle.dump(Citylist, file)

with open("SwissDistances.pkl", 'rb') as file:
    td = pickle.load(file)

convert = {}
for ci in range(len(Citys)):
    for ki in range(len(Citys[ci])):
        convert[Citys[ci][ki]] = (ci, ki)

newTd = {convert[n1]:{convert[n2]:td[n1][n2] for n2 in td[n1]} for n1 in td}

with open("Citydistances.pkl", 'wb') as file:
        pickle.dump(newTd, file)

