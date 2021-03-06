from collections import defaultdict
import sys
from Heap import Heap
import csv
import json
from Node import Node
from math import sqrt
# from google_drive_util import create_file
import cv2
from googletrans import Translator
translator = Translator()
import numpy as np
import PIL
from PIL import Image
import glob
from save_image import save_image
import matplotlib.pyplot as plt

def initialize_map(filename):
    f = open(filename)
    data = json.load(f)
    nodes = {}
    map_node = {}
    for key, node in data.items():
        temp_node = Node(
            number=int(node["Node number"]), ## dont change this to -1
            name=node["Node Name"],
            x=int(node["x_pos"]),
            y=int(node["y_pos"]),
            node_type=node["Type "],
            floor=int(node["Floor"]),
            building=node["Building"],
            map = int(node["Map Number"])

        )
        nodes[int(key)-1] = temp_node
        map_node[node["Node Name"]] = int(node["Node number"])-1
    return nodes,map_node

def get_image_mapping(filename):
    f = open(filename)
    data = json.load(f)
    images = {}
    for key, value in data.items():
        images[key] = value
    return images


class Graph:

    def __init__(self, V, nodes):
        self.V = V
        self.graph = defaultdict(list)
        self.nodes = nodes

    def calculateDistance(self, src, dest):
        return sqrt(pow(self.nodes[src].abs_x - self.nodes[dest].abs_x , 2)+pow(self.nodes[src].y-self.nodes[dest].y , 2))

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
                self.addEdge(int(row['Nodes'])-1, int(row['Adjacents'])-1)

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

    def getDirections(self, path, dest):
        directions = []
        directions_text = ""
        # print("In directions: ", path)
        for i in range(1, len(path)):
            ## case 1: for first node - only parent is considered
            if i==1:
                if path[0]== 16: #Mech Gate
                    curr = path[i]
                    prev = path[i - 1]
                    if self.nodes[curr].x > self.nodes[prev].x and self.nodes[curr].y == self.nodes[prev].y:
                        directions.append('Right')
                    elif self.nodes[curr].x < self.nodes[prev].x and self.nodes[curr].y == self.nodes[prev].y:
                        directions.append('Left')
                    elif self.nodes[curr].x == self.nodes[prev].x and self.nodes[curr].y > self.nodes[prev].y:
                        directions.append('Back')
                    elif self.nodes[curr].x == self.nodes[prev].x and self.nodes[curr].y < self.nodes[prev].y:
                        directions.append('Straight')
                    else:
                        directions.append("check em")
                elif path[0]==5:  # Girls Hostel
                    curr = path[i]
                    prev = path[i - 1]
                    if self.nodes[curr].x > self.nodes[prev].x and self.nodes[curr].y == self.nodes[prev].y:
                        directions.append('Straight')
                    elif self.nodes[curr].x < self.nodes[prev].x and self.nodes[curr].y == self.nodes[prev].y:
                        directions.append('Back')
                    elif self.nodes[curr].x == self.nodes[prev].x and self.nodes[curr].y > self.nodes[prev].y:
                        directions.append('Right')
                    elif self.nodes[curr].x == self.nodes[prev].x and self.nodes[curr].y < self.nodes[prev].y:
                        directions.append('Left')
                    else:
                        directions.append("check em")

                else: #Main Gate and default case (shouldnt be called for default!)
                    curr = path[i]
                    prev = path[i-1]
                    if self.nodes[curr].x > self.nodes[prev].x and self.nodes[curr].y == self.nodes[prev].y:
                        directions.append('Right')
                    elif self.nodes[curr].x < self.nodes[prev].x and self.nodes[curr].y == self.nodes[prev].y:
                        directions.append('Left')
                    elif self.nodes[curr].x == self.nodes[prev].x and self.nodes[curr].y > self.nodes[prev].y:
                        directions.append('Straight')
                    elif self.nodes[curr].x == self.nodes[prev].x and self.nodes[curr].y < self.nodes[prev].y:
                        directions.append('Back')
                    elif path[0] in (33, 41) or path[0] in (48, 52):
                        directions.append("Straight")
                    else:
                        directions.append("Check em")



                if(directions[-1]!='Straight'):
                    directions_text = "First turn {} and keep walking".format(directions[-1])
                else:
                    directions_text = "Walk straight"
                if(self.nodes[curr].name!=""):
                    directions_text+= " till you reach " + self.nodes[curr].name+"."
                else:
                    directions_text+="."

            else:
                x1 = self.nodes[path[i-2]].x            # x1,y1 -> x2,y2
                y1 = self.nodes[path[i-2]].y
                x2 = self.nodes[path[i-1]].x
                y2 = self.nodes[path[i-1]].y
                x3 = self.nodes[path[i]].x
                y3 = self.nodes[path[i]].y

                # Very special case of mech building passage which is slant.
                if (path[i - 1] in range(33, 40) and path[i] in range(34, 41)) or (path[i-1] in range(48,52) and path[i] in range(48,52)):
                    if (path[i - 1] == 33):
                        directions.append('Slight right')
                    else:
                        directions.append('Straight')

                elif self.nodes[path[i-1]].name=='staircase' and self.nodes[path[i]].name == 'staircase' and self.nodes[path[i]].floor != self.nodes[path[i-1]].floor:
                    floor = ""
                    if(self.nodes[path[i]].floor==1):
                        floor = "first"
                    elif self.nodes[path[i]].floor==2:
                        floor = "second"
                    elif self.nodes[path[i]].floor==3:
                        floor = "third"
                    elif self.nodes[path[i]].floor==0:
                        floor = "ground"
                    directions_text += f' Now, use the staircase to go to the {floor} floor.'

                    if i == len(path) - 1:
                        if ('washroom' in self.nodes[dest].name):
                            directions_text += " You have reached the washroom."
                        else:
                            directions_text += f"You have arrived at {nodes[path[i]].name}"
                    continue

                elif self.nodes[path[i - 2]].name == 'staircase' and self.nodes[path[i-1]].name == 'staircase' and self.nodes[path[i-1]].floor != self.nodes[path[i - 2]].floor:
                    directions_text += " Walk straight."
                    if i == len(path) - 1:
                        if ('washroom' in self.nodes[dest].name):
                            directions_text += " You have reached the washroom."
                        else:
                            directions_text += f"You have arrived at {self.nodes[path[i]].name}"
                    continue

                # Map Connectors
                elif path[i-2]==0 or path[i-1] == 0 or path[i-2]==90 or path[i-1]==90 or path[i-2]==92 or path[i-1]==92 or path[i-2]==13 or path[i-1]==13:
                    directions.append("Straight")

                elif(x2>x1 and y1==y2):
                    if(y3>y2 and x2==x3):
                        directions.append('Right')
                    elif(y2>y3 and x2==x3):
                        directions.append('Left')
                    elif(x3>x2 and y2==y3):
                        directions.append('Straight')
                    elif (x3 < x2 and y2 == y3):
                        directions.append('Back')
                    else:
                        directions.append('check em x2x1')

                elif (x2 < x1 and y1 == y2):
                    if (y3 > y2 and x2 == x3):
                        directions.append('Left')
                    elif (y2 > y3 and x2 == x3):
                        directions.append('Right')
                    elif (x3 > x2 and y2 == y3):
                        directions.append('Back')
                    elif (x3 < x2 and y2 == y3):
                        directions.append('Straight')
                    else:
                        directions.append('check em x1x2')

                elif (x2 == x1 and y1 < y2):
                    if (x3 > x2 and y2 == y3):
                        directions.append('Left')
                    elif (x2 > x3 and y2 == y3):
                        directions.append('Right')
                    elif (y3 < y2 and x2 == x3):
                        directions.append('Back')
                    elif (y3 > y2 and x2 == x3):
                        directions.append('Straight')
                    else:
                        directions.append('check em y2y1')

                elif (x2 == x1 and y1 > y2):
                    if (x3 > x2 and y2 == y3):
                        directions.append('Right')
                    elif (x2 > x3 and y2 == y3):
                        directions.append('Left')
                    elif (y3 < y2 and x2 == x3):
                        directions.append('Straight')
                    elif (y3 > y2 and x2 == x3):
                        directions.append('Back')
                    else:
                        directions.append('check em y1y2')

                else:
                    directions.append('Check em else')

                if(directions[-1]=='Straight'):
                    if directions[-2]!='Straight':
                        directions_text+=" Continue straight."
                else:
                    if(self.nodes[path[i-1]].name!=''):
                        directions_text+=" Now at {} turn {}.".format(self.nodes[path[i-1]].name, directions[-1])
                    else:
                        directions_text+=" Take the next "+ directions[-1] + "."

                if i == len(path) - 1:
                    if ('washroom' in self.nodes[dest].name):
                        directions_text += " You have reached the washroom."
                    else:
                        directions_text += f"You have arrived at {self.nodes[path[i]].name}"


        return directions, directions_text


    def dijkstra(self, src, dest):
        V = self.V
        dist = []
        minHeap = Heap()
        directions = []
        parents = [-1]*(len(self.nodes))
        path = []
        path.append(src)
        for v in range(V):
            dist.append(sys.maxsize)
            minHeap.array.append(minHeap.newMinHeapNode(v, dist[v]))
            minHeap.pos.append(v)

        minHeap.pos[src] = src
        dist[src] = 0
        minHeap.decreaseKey(src, dist[src])

        minHeap.size = V

        while minHeap.isEmpty() == False:
            newHeapNode = minHeap.extractMin()

            u = newHeapNode[0]

            for pCrawl in self.graph[(u)]:

                v = pCrawl[0]

                if minHeap.isInMinHeap(v) and dist[u] != sys.maxsize and pCrawl[1] + dist[u] < dist[v]:
                        dist[v] = pCrawl[1] + dist[u]
                        parents[v] = u
                        minHeap.decreaseKey(v, dist[v])
        path = self.getSolution(dist, parents, src, dest)
        print(dist)
        directions, directions_text = self.getDirections(path, dest)
        return round(dist[dest], 2), path, directions, directions_text


# This function is created to find washroom closest washroom
    def findDestination(self, src, dest, gender):
        #Repromt to ask girls/boys washroom
        all_dests = []
        dist = []
        if(dest=="washroom"):
            for i in range(len(nodes)):
                if "washroom" in nodes[i].name and gender in nodes[i].name:
                    all_dests.append(nodes[i])
                    distance, _, _, _ = self.dijkstra(map_node[src], nodes[i].number)
                    dist.append(distance)
        else:
            for i in range(len(nodes)):
                if dest in nodes[i].name :
                    all_dests.append(nodes[i])
                    distance, _, _, _ = self.dijkstra(map_node[src], nodes[i].number)
                    dist.append(distance)

        dest = all_dests[dist.index(min(dist))]
        return dest.number



def getPath(destination,source, gender="null"):
    print(source + " -->" + str(destination))
    src_number = map_node[source]
    dest_number = graph.findDestination(source, destination, gender)
    if dest_number:
        distance, path, directions, directions_text = graph.dijkstra(src_number, dest_number)
        directions_text +=("You have walked a total of "+str(int(distance*650/2400))+"meters") #convert pixel to meters => length of college in px to meteres

        MAX_SIZE = (24, 24) ## for thumbnail
        path_color = (0, 0, 0, 255) ##black path
        line_thickness = 2

        img = PIL.Image.open(f'resized-new/{nodes[src_number].map}-{nodes[src_number].floor}.jpg')
        img = np.array(img)
        img_temp = PIL.Image.fromarray(img)
        curr_map = nodes[src_number].map
        curr_floor = nodes[src_number].floor
        counter = 0
        src_map = nodes[src_number].map
        dest_map = nodes[dest_number].map
        src_floor = nodes[src_number].floor
        dest_floor = nodes[dest_number].floor
        print("PATH: ", path)
        for i in range(len(path)-1):
            p1 = nodes[path[i]]
            p2 = nodes[path[i+1]]

            if i==0 and (src_map!=dest_map or src_floor!=dest_floor):
                src_img = PIL.Image.open('dest.png')
                src_img.thumbnail((28, 28))
                w, h = src_img.size
                paste_src_x = nodes[src_number].x - w // 2
                paste_src_y = nodes[src_number].y - h + 2
                img_temp.paste(src_img, (paste_src_x, paste_src_y))
                img = np.array(img_temp)

            if (curr_map!=p1.map or curr_floor!=p1.floor):
                img = np.array(img_temp)
                # plt.imshow(img)
                # plt.show()
                # cv2.imwrite(f"all-dest/{src_number}-{dest_number}-{counter}.jpg", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                cv2.imwrite(f"temp-output/{src_number}-{dest_number}-{curr_map}-{curr_floor}-{counter}.jpg", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                counter+=1
                curr_map = p1.map
                curr_floor = p1.floor
                img = PIL.Image.open(f'resized-new/{curr_map}-{curr_floor}.jpg')
                img = np.array(img)
                img_temp = PIL.Image.fromarray(img)

            len_line = abs(p1.x-p2.x) + abs(p1.y-p2.y)

            if len_line==0:
                len_line=1

            if i==len(path)-2:
                # arrow in middle
                mid_point = ((p1.x + p2.x)//2, (p1.y + p2.y)//2)
                ## two lines
                cv2.arrowedLine(img, (p1.x, p1.y), mid_point, color=path_color, thickness=line_thickness, tipLength=13 * 2/ len_line)
                cv2.line(img, mid_point, (p2.x, p2.y), path_color, thickness=line_thickness, lineType=cv2.LINE_AA)
                if src_map!=dest_map or src_floor!=dest_floor:
                    img_temp = PIL.Image.fromarray(img)
                    dest_img = PIL.Image.open('src.png')
                    dest_img.thumbnail(MAX_SIZE)
                    w, h = dest_img.size
                    paste_dest_x = nodes[dest_number].x - w // 2
                    paste_dest_y = nodes[dest_number].y - h + 2
                    img_temp.paste(dest_img, (paste_dest_x, paste_dest_y))
                    img = np.array(img_temp)
            elif(p2.map==p1.map and p2.floor==p1.floor):
                cv2.arrowedLine(img, (p1.x, p1.y), (p2.x, p2.y), color=path_color, thickness=line_thickness, tipLength=13 / len_line)
                img_temp = PIL.Image.fromarray(img)

        ## if both dest and source are on same map
        if src_map==dest_map and src_floor==dest_floor:
            img_temp = PIL.Image.fromarray(img)

            ## adding source marker
            src_img = PIL.Image.open('dest.png')
            src_img.thumbnail((28, 28))
            w, h = src_img.size
            paste_src_x = nodes[src_number].x - w // 2
            paste_src_y = nodes[src_number].y - h + 2
            img_temp.paste(src_img, (paste_src_x, paste_src_y))

            # adding destination marker
            dest_img = PIL.Image.open('src.png')
            dest_img.thumbnail(MAX_SIZE)
            w, h = dest_img.size
            paste_dest_x = nodes[dest_number].x - w // 2
            paste_dest_y = nodes[dest_number].y - h + 2
            img_temp.paste(dest_img, (paste_dest_x, paste_dest_y))

        print(src_number, " ", dest_number, " ", counter)

        # display image
        img = np.array(img_temp)

        # plt.imshow(img)
        # plt.show()
        # cv2.imwrite(f"all-dest/{src_number}-{dest_number}-{counter}.jpg", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        cv2.imwrite(f"temp-output/{src_number}-{dest_number}-{curr_map}-{curr_floor}-{counter}.jpg",
                    cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        print(distance)
        print(directions_text)

        # for saving final image
        count = 0
        output_images = []

        ## TODO: change to whatever path we're reading from in actual appln
        for name in glob.glob(f'C:\\Users\\Ritu\\PycharmProjects\\VJTI-Navigation\\temp-output\\{src_number}-{dest_number}-*'):
            print(name)
            count +=1
            output_images.append(name)

        ## for alignment of maps 2-0 2-1 special cases
        case2 = True
        if src_map==2 and dest_map==2 and src_floor==1 and dest_floor==0:
            case2 = False
        save_image(output_images, count, src_number, dest_number, case2)
        return directions_text
    return ""



""" Library Path Test
getPath("Comps dept","Staircase main bldg/statue")
getPath("BEE Lab","Comps dept")
getPath("library staircase","BEE Lab")
getPath("library staircase","Staircase main bldg/statue")
"""

"""
Hindi Skill Code
text = getPath("Library","Staircase main bldg/statue")
print(text)
text = text.replace("Take the next Left","Take the next left turn")
text = text.replace("Take the next Right","Take the next right turn")
print(text)
result = translator.translate(text,src='en', dest='hi')
print(result.text)
"""
# img = Image.open('new-ss/FINISHED/2-0.PNG')
# plt.imshow(img)
# for i in range(len(nodes)):
#     for j in graph.graph[i]:
#         v = j[0]
#         if(nodes[i].map==2 and nodes[v].map ==2 and nodes[i].floor==0 and nodes[v].floor==0):
#             plt.plot(nodes[i].x, nodes[i].y, 'o')
#             plt.plot(nodes[v].x, nodes[v].y, 'o')
#             plt.plot([nodes[i].x, nodes[v].x], [nodes[i].y, nodes[v].y])
#             plt.text(nodes[i].x + 10, nodes[i].y, i+ 1)

# plt.show()

nodes, map_node = initialize_map('nodes.json')
graph = Graph(len(nodes), nodes)
graph.addAllEdges('edges.csv')

img = Image.open('resized-new/2-0.jpg')
plt.imshow(img)
for i in range(len(nodes)):
    for j in graph.graph[i]:
        v = j[0]
        if(nodes[i].map==2 and nodes[v].map == 2  and nodes[i].floor==0 and nodes[v].floor==0):
            plt.plot(nodes[i].x, nodes[i].y, 'o')
            plt.plot(nodes[v].x, nodes[v].y, 'o')
            plt.plot([nodes[i].x, nodes[v].x], [nodes[i].y, nodes[v].y])
            plt.text(nodes[i].x + 10, nodes[i].y, i+ 1)
plt.show()

# TESTCASES FOR MAP #2
# print(getPath("BCT Lab","statue"))
# print(getPath("Xerox Center","statue"))
# print(getPath("girls washroom","director office"))

# # TESTCASES FOR MAP #1
# print(getPath( "Girls hostel", "Football Field"))
# print(getPath("Girls hostel", "Boys hostel 1"))

# TESTCASES FOR MAP #3
# print(getPath( "Xerox Center","Mech Gate"))
# print(getPath("Inside workshop #1", "Mech Building Entrance"))
# print(getPath( "director office", "Main Seminar Hall"))
# print(getPath( "Quad", "Main Seminar Hall"))

# TESTCASES FOR MAP #4
# print(getPath("main gate", "dep1"))

# TESTCASES FOR WASHROOM
# print(getPath("washroom","main gate",  "girls"))

# # TESTCASES FOR MULTIPLE MAPS
# print(getPath("Cricket Ground", "main gate"))
# print(getPath("Main Seminar Hall", "Cricket Ground"))
import time
## generating all output maps
# with open('locations.csv', 'r') as read_obj:
#     # pass the file object to reader() to get the reader object
#     csv_reader = csv.reader(read_obj)
#     # Pass reader object to list() to get a list of lists
#     loc = list(csv_reader)
#     for i in range(len(loc)):
#         loc[i]= "".join(loc[i])
#     print(loc)
#     st = time.time()
#     for i in range(len(loc)):
#         for j in range(len(loc)):
#             if(map_node[loc[i]] not in range(34, 41)):
#                 print(getPath(loc[i], loc[j]))
#             if (map_node[loc[j]] not in range(34, 41)):
#                 print(getPath(loc[j], loc[i]))
#
#     end = time.time()
#     print("Time taken: ", str(end-st), "s")
#
#

# import time
# logs = open('direction_logs.logs', 'w')
# with open('locations.csv', 'r') as read_obj:
#     # pass the file object to reader() to get the reader object
#     csv_reader = csv.reader(read_obj)
#     # Pass reader object to list() to get a list of lists
#     loc = list(csv_reader)
#     for i in range(len(loc)):
#         loc[i]= "".join(loc[i])
#     print(loc)
#     st = time.time()
#     for i in range(len(loc)):
#         for j in range(len(loc)):
#             if(map_node[loc[i]] not in range(34, 41)):
#                 logs.write(f"Source: {loc[i]}, Destination: {loc[j]}, Path: {getPath(loc[i], loc[j])}\n\n")
#             if (map_node[loc[j]] not in range(34, 41)):
#                 logs.write(f"Source: {loc[j]}, Destination: {loc[i]}, Path: {getPath(loc[j], loc[i])}\n\n")
#
#     end = time.time()
#     print("Time taken: ", str(end-st), "s")
#

getPath("washroom","blockchain lab", "girls")