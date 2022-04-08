import time

def updateLoc(route):

    # while True:
    #     try:
    #         if len(route['route'][0]) == 0:
    #             del route['route'][0]
    #             del route['dist'][0]
    #             del route['path'][0]

    #         print(sum(route['dist'])) # left how much
    #         print(route['route'][0][0])
    #         print(route['path'])
    #         del route['route'][0][0]
    #     except IndexError:
    #         print('Completed')
    #         break
    #     time.sleep(0.1)
    retInfo = {}
    try:
        if len(route['route'][0]) == 0:
            del route['route'][0]
            del route['dist'][0]
            del route['path'][0]

        retInfo['dist'] = (sum(route['dist'])) # left how much
        retInfo['loc'] = route['route'][0][0]
        retInfo['vt'] = route['path']
        del route['route'][0][0]
    except IndexError:
        # print('Completed')
        return None


# printRoute(route1)

# print(route1)
# format OUT
# map key 'path':list, 'route':list of list(each edge) of tuples(cood), 'dist':list of edge dist, 'totaldist':int

# print(onroad)

randomloc = vt['50']

def heuristicAlgo(node, pax, pool, type):

    candidates = []

    for i in onroad:
        loc = i['route']['path'][0] # vertex number
        if not i['spaceleft'] < pax and i['details']['pool'] == pool and i['details']['type'] == type:
            candidates.append(
                {
                    'id':i['id'],
                    'loc':loc,
                    'dist':999999,
                    }
            )

    if len(candidates) < 1:
        return None

    bestFit = candidates[0]

    while True:
        idx = randint(0, len(candidates)-1)
        candidate = candidates[idx]
        dist = graph2.getShortestPath(node, candidate['loc'], edges2)['totaldist']
        candidate['dist'] = dist
        if candidate['dist'] < bestFit['dist']:
            bestFit = candidate

        print(dist, bestFit)
        if dist < 4167:
            break
        del candidates[idx]
        if len(candidates) < 1:
            break

    return bestFit
    

print(heuristicAlgo('5', 3, True, 'standard'))

def getRoute():
    start = '7'
    end = '80'
    pax = 4
    pool = False
    type = 'family'

    driver = heuristicAlgo(start, pax, pool, type)
    if driver == None:
        return None
    driverToPaxRoute = graph1.getShortestPath(driver['loc'], start, edges1)
    paxRoute = graph1.getShortestPath(start, end, edges1)
    return {
        'driver': driverToPaxRoute,
        'pax': paxRoute
    }

def getSharedRoute():

    start1 = '7'
    end1 = '10'
    start2 = '9'
    end2 = '13'

    # get different permutations


print(getRoute())