import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import thread



#Creating events:
def event(events,hold):
    #Initialize source, destination, arrival time, holding time arrays
    source = np.zeros(events,dtype=np.int8)
    destination = np.zeros(events, dtype=np.int8)

    #Assign source and destination for each lightpath
    for i in range(events):
        source[i] = np.random.uniform(1,7)
        destination[i] = np.random.uniform(1,7)
        while(destination[i]==source[i]):
            destination[i] = np.random.uniform(1,7)

    # Mean hold time:
    hold = hold  # 1/lambda
    holding = np.random.exponential(hold, events)

    event = np.vstack((source, destination,holding)).T
    return event

def arrival(events,arrival):
    # Mean interarrval and hold time:
    interarrival = arrival  # 1/lambda
    arrival = np.random.exponential(interarrival, events)
    return arrival


def freePath(event,G):
    path = nx.shortest_path(G, source=event[0], target=event[1])
    return path

def freeWavelength(path):
    wavelength = []
    for i in range(len(path) -1 ):
        free = []
        for j in range(2):
            available = G[path[i]][path[i+1]][j+1]['available']
            if (available>0):
                if (j+1) not in free:
                    free.append(j+1)
        wavelength.append(free)
    freeWavelength = wavelength[0]
    for i in range(len(path)-1):
        freeWavelength = set(freeWavelength) & set(wavelength[i])
    return np.array(list(freeWavelength))

def checkBlocking(freeWavelength):
    if (len(freeWavelength) == 0):
        return False #If blocked
    else:
        return True #If NOT blocked

def assignWavelength(freeWavelength):
    wavelength = np.random.choice(freeWavelength)
    return wavelength

def Transmission(event,wavelength,path,G):
    for i in range(len(path)-1):
        nx.set_edge_attributes(G, 'available', {(path[i],path[i+1],wavelength): (G[path[i]][path[i+1]][wavelength]['available'] - 1)})
    #print G.edges(data=True)
    start_time = time.time()
    while(True):
        elapsed_time = time.time() - start_time
        #print elapsed_time
        if (elapsed_time>=event[2]):
            break
    for i in range(len(path) - 1):
        nx.set_edge_attributes(G, 'available', {(path[i],path[i+1],wavelength): (G[path[i]][path[i+1]][wavelength]['available'] + 1)})
    #print G.edges(data=True)

# def Release(wavelength,path,G):
#     for i in range(len(path) - 1):
#         nx.set_edge_attributes(G, 'available', {(path[i], path[i + 1], wavelength): (G[path[i]][path[i + 1]][wavelength]['available'] + 1)})

G = nx.MultiGraph()

for i in range(6):
    G.add_node(i+1)

#Add edges:
for i in range(5):
    for j in range(2):
        G.add_edge(i+1,i+2,key=j+1,available=2)

for j in range(2):
    G.add_edge(1,6,key=j+1,available=2)
    G.add_edge(2,5,key=j+1,available=2)

#Checking:
# print "Nodes"
# print G.nodes(data=True)
# print "Edges"
# print G.edges(data=True)

#Draw the graph
pos = nx.spring_layout(G)
nx.draw(G,pos,with_labels=True)
plt.show()


def running(event,arrival,multiplier):
    blocking = 0

    event = event(200,1*multiplier)
    print event

    arrival= arrival(200,0.1)
    print arrival

    i = 0
    while(True):
        start_time = time.time()
        while(True):
            elapsed_time = time.time() - start_time
            # print elapsed_time
            if (elapsed_time >= arrival[i]):
                break
        current_event = event[i]
        path = freePath(current_event,G)
        print i+1
        print path
        free_Wavelength = freeWavelength(path)
        if (checkBlocking(free_Wavelength)):
            #print "test"
            wavelength = assignWavelength(free_Wavelength)
            #print wavelength
            thread.start_new_thread(Transmission,(current_event,wavelength, path, G))
            #Transmission(current_event,wavelength, path, G)
            # except:
            #     print "Error: unable to start thread"
        else:
            blocking +=1
        i+=1
        if (i>(len(event)-1)):
            break
    return blocking

blocking = np.zeros(10)
for i in range(10):
    blocking[i] = running(event,arrival,i+1)
print blocking
blocking = blocking/200
ratio = [10,20,30,40,50,60,70,80,90,100]

# calculate polynomial
z = np.polyfit(ratio, blocking, 3)
f = np.poly1d(z)

# calculate new x's and y's
ratio_new = np.linspace(ratio[0], ratio[-1], 50)
blocking_new = f(ratio_new)

plt.plot(ratio,blocking,'o', ratio_new, blocking_new)
plt.xlim([ratio[0]-1, ratio[-1] + 1 ])
plt.show()


# print "Edges"
# print G.edges(data=True)
# nx.set_edge_attributes(G,'available',{(1,2,1):(G[1][2][1]['available']-1)})
# print "Edges"
# print G.edges(data=True)

# event = [1,4,0.1]
# path =  freePath(event,G)
# print path
# freeWavelength = freeWavelength(path)
# print freeWavelength
# wavelength = assignWavelength(freeWavelength)
# print wavelength
# Transmission(event,wavelength,path,G)