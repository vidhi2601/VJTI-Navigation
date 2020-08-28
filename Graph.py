from collections import defaultdict
import sys
from Heap import Heap
import csv
import json
import re
from Node import Node
from math import sqrt


def initialize_map(filename):
    f = open(filename)
    data = json.load(f)
    nodes = {}
    for key, node in data.items():
        temp_node = Node(
            number=node["number"], ## dont change this to -1
            name=node["name"],
            x=int(node["x"]),
            y=int(node["y"]),
            node_type=node["type"],
            floor=int(node["floor"]),
            building=node["building"]
        )
        nodes[int(key)-1] = temp_node
    return nodes


class Graph():

    def __init__(self, V, nodes):
        self.V = V
        self.graph = defaultdict(list)
        self.nodes = nodes

    def calculateDistance(self, src, dest):
        return sqrt(pow(nodes[src].x - nodes[dest].x, 2)+pow(nodes[src].y-nodes[dest].y, 2))

    def addEdge(self, src, dest):
        weight = self.calculateDistance(src, dest)
        # print(src, dest, weight)
        newNode = [dest, weight]
        self.graph[src].insert(0, newNode)
        newNode = [src, weight]
        self.graph[dest].insert(0, newNode)

    def addAllEdges(self, input_file):
        with open(input_file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.addEdge(int(row['Node '])-1, int(row['Adjacents'])-1)

    def getPath(self, parent, j, path):
        if parent[j] == -1 :
            return
        self.getPath(parent , parent[j], path)
        # print (j, "\t", self.nodes[j].name)
        path.append(j)


    def getSolution(self, dist, parent, source, dest):
        # print("Vertex \t\tDistance from Source\tPath")
        path = []
        path.append(source)
        self.getPath(parent, dest, path)
        print()
        return path

    def dijkstra(self, src, dest):
        V = self.V
        dist = []
        minHeap = Heap()
        directions = [] ## for directions - revathi
        parents = [-1]*(len(self.nodes)) ## for path - revathi
        path = []
        path.append(src)
        for v in range(V):
            dist.append(sys.maxsize)
            minHeap.array.append( minHeap.newMinHeapNode(v, dist[v]))
            minHeap.pos.append(v)

        minHeap.pos[src] = src
        dist[src] = 0
        minHeap.decreaseKey(src, dist[src])

        minHeap.size = V

        #TODO: modify to show proper route -- done revathi
        while minHeap.isEmpty() == False:
            newHeapNode = minHeap.extractMin()

            u = newHeapNode[0]

            for pCrawl in self.graph[(u)]:
                v = pCrawl[0]
                if minHeap.isInMinHeap(v) and dist[u] != sys.maxsize and pCrawl[1] + dist[u] < dist[v]:
                        dist[v] = pCrawl[1] + dist[u]
                        parents[v] = u
                        minHeap.decreaseKey(v, dist[v])
        path = self.getSolution(dist, parents, source, dest)
        return round(dist[dest], 2), path

    #TODO: add directions switch case

## driver code to test
if __name__=='__main__':

    source = 19
    dest = 0

    ##TODO: code to redirect to nearest staircase - pseudo code written
    # if nodes[dest].floor==1:
    #     for node in adj_list of dest
    #         if re.find('staircase') in nodes[dest].name:
    #             dest = that node

    nodes = initialize_map('nodes.json')
    print(nodes)

    graph = Graph(34, nodes)
    graph.addAllEdges('edges.csv')
    distance, path = graph.dijkstra(source, dest)

    print("Source: ", source, " ", nodes[source].name)
    print("Destination: ", dest, " ", nodes[dest].name)
    print("Path: ", path)
    for i in range(len(path)):
        if nodes[path[i]].name=="":
            continue
        if i!=len(path)-1:
            print(nodes[path[i]].name, end=" -- > ")
        else:
            print(nodes[path[i]].name)
