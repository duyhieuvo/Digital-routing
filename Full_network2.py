import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time

def Event(events):
    source = np.zeros(events, dtype=np.int8)
    destination = np.zeros(events, dtype=np.int8)

    # Assign source and destination for each lightpath
    for i in range(events):
        source[i] = np.random.uniform(1,18)
        destination[i] = np.random.uniform(1,18)
        while (destination[i] == source[i]):
            destination[i] = np.random.uniform(1, 18)

    event = np.vstack((source, destination)).T
    return event

def timeline(events,arrival,hold):
    time = np.zeros((events*2,3))
    entering = np.zeros(events)
    entering[0]= np.random.exponential(arrival)
    for i in range(1,events):
        entering[i] = entering[i-1] + np.random.exponential(arrival)
    holding = np.random.exponential(hold, events)
    leaving = entering + holding
    for i in range(events):
        time[i][0]=entering[i]
        time[i][1]=0 #0 indicates entering
        time[i][2]=i
    for i in range(events,events*2):
        time[i][0]=leaving[i-events]
        time[i][1]=1 #1 indicates leaving
        time[i][2]=(i-events)

    time = time[time[:,0].argsort()]
    return time


def freePath(event,G):
    path = nx.all_shortest_paths(G, source=event[0], target=event[1])
    return list(path)

def freeWavelength(path):
    remaining = np.zeros((len(path)-1,8))
    for i in range(len(path) -1 ):
        for j in range(8):
            available = G[path[i]][path[i+1]][j+1]['available']
            if (available > 0):
                remaining[i][j]=available
            elif (available <=0):
                remaining[i][j]=0
    ratio = np.zeros(8)
    for i in range(8):
        if(np.all(remaining[:,i])):
            ratio[i] = np.sum(remaining[:,i])

    if(np.sum(ratio)!=0):
        ratio = ratio/np.sum(ratio)
    #print ratio
    return ratio

def checkBlocking(freeWavelength):
    if (not np.any(freeWavelength)): #np.any: return false if all are zeros => not np.any return true if all are zeros
        return False #If blocked
    else:
        return True #If NOT blocked

def assignWavelength(freeWavelength):
    wavelength = np.random.choice([1,2,3,4,5,6,7,8],p = freeWavelength)
    return wavelength

def Transmission(wavelength,path,G):
    for i in range(len(path)-1):
        nx.set_edge_attributes(G, 'available', {(path[i],path[i+1],wavelength): (G[path[i]][path[i+1]][wavelength]['available'] - 1)})

def Release(wavelength,path,G):
    for i in range(len(path) - 1):
        if (G[path[i]][path[i + 1]][wavelength]['available'] < 2):
            nx.set_edge_attributes(G, 'available', {(path[i],path[i+1],wavelength): (G[path[i]][path[i+1]][wavelength]['available'] + 1)})






#Function to create the graph
def createGraph():
    #Create an empty graph with no nodes and no edges
    G = nx.MultiGraph(nation ="Germany")

    #Add nodes:
    cities = ["Hamburg", "Berlin", "Leipzig", "Nuernberg", "Muenchen", "Ulm", "Stuttgart",\
              "Karlsruhe", "Mannheim", "Frankfurt", "Koeln", "Duesseldorf", "Essen", \
              "Dortmund", "Norden", "Bremen", "Hannover"]
    for i in range(17):
        G.add_node(i+1,city=cities[i])

    #Add edges:
    for i in range(16):
        for j in range(8):
            G.add_edge(i+1,i+2,key=j+1,available=2)

    for j in range(8):
        G.add_edge(1, 16, key=j + 1, available=2)
        G.add_edge(17, 1, key=j + 1, available=2)
        G.add_edge(17, 2, key=j + 1, available=2)
        G.add_edge(17, 3, key=j + 1, available=2)
        G.add_edge(17, 10, key=j + 1, available=2)
        G.add_edge(17, 14, key=j + 1, available=2)
        G.add_edge(10, 3, key=j + 1, available=2)
        G.add_edge(10, 4, key=j + 1, available=2)
        G.add_edge(7, 4, key=j + 1, available=2)

    return G

G= createGraph()
# Plot the graph
pos = nx.spring_layout(G)
nx.draw(G, pos)
node_labels = nx.get_node_attributes(G, 'city')
nx.draw_networkx_labels(G, pos, node_labels)
plt.show()


def running(G,events,multiplier,Event,timeline,freePath,freeWavelength,checkBlocking,assignWavelength,Transmission,Release):
    assignment = []

    event = Event(events)
    print event

    timeLine = timeline(events,0.01,1*multiplier)
    print timeLine

    i = 0
    k = 0
    blocking = 0
    start_time = time.time()
    while (True):
        while (True):
            elapsed_time = time.time() - start_time
            if (elapsed_time >= timeLine[i][0]):
                break
        if (timeLine[i][1]==0):
            current_event = event[k]
            path = freePath(current_event, G)
            print k + 1
            for j in range(len(path)):
                free_Wavelength = freeWavelength(path[j])
                if (checkBlocking(free_Wavelength)):
                    wavelength = assignWavelength(free_Wavelength)
                    list = [wavelength]
                    list.append(path[j])
                    assignment.append(list)
                    Transmission(wavelength,path[j],G)
                    break
                if (j == (len(path)-1)):
                    assignment.append(0)
                    blocking+=1
            k+=1
        elif(timeLine[i][1]==1):
            event_number = int(timeLine[i][2])
            if(assignment[event_number]!=0):
                Release(assignment[event_number][0],assignment[event_number][1],G)
        i+=1
        if (i==events*2):
            break
    return blocking

# blocking = running(G,10000,Event,timeline,freePath,freeWavelength,checkBlocking,assignWavelength,Transmission,Release)
# print (blocking)

blocking = np.zeros(5)
for i in range(5):
    blocking[i] = running(G,10000,i+1,Event,timeline,freePath,freeWavelength,checkBlocking,assignWavelength,Transmission,Release)
print blocking
blocking = blocking/10000
ratio = [100,200,300,400,500]

# calculate polynomial
z = np.polyfit(ratio, blocking, 3)
f = np.poly1d(z)

# calculate new x's and y's
ratio_new = np.linspace(ratio[0], ratio[-1], 50)
blocking_new = f(ratio_new)

plt.plot(ratio,blocking,'o', ratio_new, blocking_new)
plt.xlim([ratio[0]-1, ratio[-1] + 1 ])
plt.show()
