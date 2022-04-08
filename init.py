# file to initialize all global variables and key functions and data from external sources
# run this file before the main program
# import libraries
import json
import polyline
import sqlite3
import logging
import djikstra
from random import randint

# loaddata class with static methods
# initialize loadData class
class loadData:
    # get vertex data in map form, key(vertex node):value(vertex coordinates in latlong)
    def getVertexes():
        try:
            vt = open('./data/vt.json')
            ret = json.load(vt)
            vt.close()
            return ret
        except:
            return None

    # get edges data in list form (of maps)
    def getEdges(increment):
        try:
            file = open('./data/edges.json')
            data = json.load(file)
            file.close()
            edges = {}
            for i in data:
                e = i['vFrom'] + ',' + i['vTo']
                dist = i['dist']
                if randint(0,10) > 5:
                    dist *= increment
                edges[e] = {
                    'dist': dist,
                    'polyline': polyline.decode(i['polyline'])
                }
            return edges
        except:
            return None

# initialize database
class loadDb:
    def __init__(self):
        self.db_path = 'project.db'
        self.db = sqlite3.connect(self.db_path, check_same_thread = False)
        if self.healthCheck():
            logging.info(self.db_path + "Open success")
        else:
            logging.info(self.db_path + "Open failed, " + "Terminating program..")
            exit(1)
        
    def healthCheck(self):
        return self.db.total_changes == 0


# pathing algo using djikstra
# initialize pathAlgo class
class pathAlgo:
    def __init__(self, vt, edges):
        graph = {}
        nodes = [x for x in vt.keys()]
        for node in nodes:
            graph[node] = {}
        for k, v in edges.items():
            graph[k.split(',')[0]][k.split(',')[1]] = v['dist']
        self.graph = djikstra.Graph(nodes, graph)

    ## return route info and dist
    # get shortest path using djikstra algo
    def getShortestPath(self, startNode, endNode, edges):
        retInfo = {
            'path' : [],
            'counter':[],
            'route': [],
            'dist': [],
            'totaldist': 0,
        }
        prev, _ = djikstra.dijkstraAlgorithm(graph=self.graph, startNode=startNode)
        res = djikstra.retResult(prev, startNode=startNode, targetNode=endNode)
        retInfo['path'] = res
        for i in range(len(res) - 1):
            try:
                idx = res[i] + ',' + res[i+1]
                retInfo['counter'].append(len(edges[idx]['polyline']))
                retInfo['route'] += edges[idx]['polyline']
                retInfo['dist'].append(edges[idx]['dist'])
                retInfo['totaldist'] += edges[idx]['dist']
            except:
                idx = res[i+1] + ',' + res[i]
                retInfo['counter'].append(len(edges[idx]['polyline']))
                retInfo['route'] += edges[idx]['polyline'][::-1]
                retInfo['dist'].append(edges[idx]['dist'])
                retInfo['totaldist'] += edges[idx]['dist']
        return retInfo
#class for drivers
class drivers:
    #initialize data for drivers
    def __init__(self):
        file = open('./data/drivers.json')
        self.data = json.load(file)
        file.close()
    #generates random routes
    def randomRoute(graph, edge, vt):
        # get random vertexes for start and end
        start = randint(1, len(vt))
        end = start
        # make sure start and end is different
        while end == start:
            end = randint(1, len(vt))
        route = graph.getShortestPath(
            str(start), str(end), edge
        )
        return route
    

# load vertexes
vt = loadData.getVertexes()

# in the format of
# "3,5":{
#   'dist':-,
#   'polyline':-    
# }
edges1 = loadData.getEdges(1)

# random increase in edges to simulate fastest and shortest paths
edges2 = loadData.getEdges(3)        

# database store
store = loadDb().db

# load initial graph
graph1 = pathAlgo(vt, edges1) # shortest route
graph2 = pathAlgo(vt, edges2) # fastest route

# format for getting route

route1 = graph1.getShortestPath('22', '83', edges1)
# print(route1)

# init onroad
cars = drivers().data
onroad = []

# init the randomroute for the drivers
for k,v in cars.items():
    onroad.append(
        {
            'id':k,
            'details': v,
            'route':drivers.randomRoute(graph1, edges1, vt),
            'spaceleft':v['space']
        }
    )

# own implementation of heuristic algo
# choose an initial pool of candidates (taxi drivers)
# randomly choose a driver
# calculate the distance to each driver (using djikstra)
# terminate if conditions met
# if not choose the best candidates
def heuristicAlgo(node, pax, type):
    # select initial candidates pool
    candidates = []
    # loop through to get candidates pool
    for i in onroad:
        loc = i['route']['path'][0] # vertex number
        if not i['spaceleft'] < pax and i['details']['type'] == type:
            candidates.append(
                {
                    'id':i['id'],
                    'loc':loc,
                    'dist':999999, # add default max distance 
                    }
            )
    # if no candidates return none
    if len(candidates) < 1:
        return None
    # assign initial bestfit
    bestFit = candidates[0]
    # initiate loop to get bestfit
    while True:
        # get random index
        idx = randint(0, len(candidates)-1)
        # get initial candidate 
        candidate = candidates[idx]
        # get distance by using djistra
        dist = graph2.getShortestPath(node, candidate['loc'], edges2)['totaldist']
        candidate['dist'] = dist
        # compare if candidate dist better than bestfit dist
        if candidate['dist'] < bestFit['dist']:
            # assign bestfit to candidate if so
            bestFit = candidate 
        
        # if distance less than 4167, or 5mins drive at 50km/h
        if dist < 4167:
            # break loop
            break
        # delete candidate from index
        del candidates[idx]
        # break if len is less than 1
        if len(candidates) < 1:
            break
    # return bestfit
    return bestFit

# print(heuristicAlgo('5', 2, 'standard'))

# get the shortest shared route based on the number of pax
def sharedRoute(s1, e1, s2, e2):
    # first route permuatation
    r11 = graph1.getShortestPath(s1, e1, edges1)
    r12 = graph1.getShortestPath(s2, e2, edges1)
    r13 = graph1.getShortestPath(e1, s2, edges1)
    # first route total distance
    r1d = r11['totaldist'] + r12['totaldist'] + r13['totaldist']

    # 2nd route permutation
    r21 = graph1.getShortestPath(s1, s2, edges1)
    r22 = graph1.getShortestPath(s2, e1, edges1)
    r23 = graph1.getShortestPath(e1, e2, edges1)
    # 2nd route total distance
    r2d = r21['totaldist'] + r22['totaldist'] + r23['totaldist']

    # 3rd route permutation
    r31 = graph1.getShortestPath(s1, s2, edges1)
    r32 = graph1.getShortestPath(s2, e2, edges1)
    r33 = graph1.getShortestPath(e2, e1, edges1)
    # 3rd route total distance
    r3d = r31['totaldist'] + r32['totaldist'] + r33['totaldist']
    # if r1 less than r2 or r1 less than r3
    if r1d > r2d or r1d > r3d:
        # do not pick passenger up
        return None
    # else returns the optimal route as list
    elif r2d < r3d:
        return [r21,r22,r23]
    else:
        return [r31,r32,r33]


