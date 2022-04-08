import sys

class Graph(object):
    def __init__(self, nodes, initGraph):
        self.nodes = nodes
        self.graph = self.constructGraph(nodes, initGraph)
        
    def constructGraph(self, nodes, initGraph):
        # make sure edges both way as undirected
        graph = {}
        for node in nodes:
            graph[node] = {}
        
        graph.update(initGraph)
        
        for node, edges in graph.items():
            for adjacentNode, value in edges.items():
                if graph[adjacentNode].get(node, False) == False:
                    graph[adjacentNode][node] = value
                    
        return graph
    
    def getNodes(self):
        # return nodes of graph
        return self.nodes
    
    def getOutgoingEdges(self, node):
        # get node neighbours
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections
    
    def value(self, node1, node2):
        "Returns the value of an edge between two nodes."
        return self.graph[node1][node2]

def retResult(previousNodes, startNode, targetNode):
    path = []
    node = targetNode
    
    while node != startNode:
        path.append(node)
        node = previousNodes[node]
 
    # Add the start node manually
    path.append(startNode)
    
    # print("We found the following best path with a value of {}.".format(shortestPath[targetNode]))
    # print(" -> ".join(reversed(path)))

    return list(reversed(path))


def dijkstraAlgorithm(graph, startNode):
    unvisitedNodes = list(graph.getNodes())
 
    # We'll use this dict to save the cost of visiting each node and update it as we move along the graph   
    shortestPath = {}
 
    # We'll use this dict to save the shortest known path to a node found so far
    previousNodes = {}
 
    # We'll use max_value to initialize the "infinity" value of the unvisited nodes   
    max_value = sys.maxsize
    for node in unvisitedNodes:
        shortestPath[node] = max_value
    # However, we initialize the starting node's value with 0   
    shortestPath[startNode] = 0
    
    # The algorithm executes until we visit all nodes
    while unvisitedNodes:
        # The code block below finds the node with the lowest score
        currentMinNode = None
        for node in unvisitedNodes: # Iterate over the nodes
            if currentMinNode == None:
                currentMinNode = node
            elif shortestPath[node] < shortestPath[currentMinNode]:
                currentMinNode = node
                
        # The code block below retrieves the current node's neighbors and updates their distances
        neighbors = graph.getOutgoingEdges(currentMinNode)
        for neighbor in neighbors:
            tentativeValue = shortestPath[currentMinNode] + graph.value(currentMinNode, neighbor)
            if tentativeValue < shortestPath[neighbor]:
                shortestPath[neighbor] = tentativeValue
                # We also update the best path to the current node
                previousNodes[neighbor] = currentMinNode
 
        # After visiting its neighbors, we mark the node as "visited"
        unvisitedNodes.remove(currentMinNode)
    
    # print('prev nodes: ', previous_nodes)
    # print('shortest path: ', shortest_path)
    return previousNodes, shortestPath
