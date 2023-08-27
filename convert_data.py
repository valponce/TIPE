import pickle

with open("D:\TIPE\SwissSimpleGraph.pkl", 'rb') as file:
    graph, coords, clusters, nodeToclusters = pickle.load(file)
Citylist=[[coords[k] for k in c] for c in clusters]

with open("Citylist.pkl", 'wb') as file:
        pickle.dump(Citylist, file)
