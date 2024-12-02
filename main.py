import xmltodict as xtd
import webbrowser
import os
import sys
import numpy as np
import folium
import parseOSM

parsing_output = parseOSM.parseOSM("./maps/map.osm")
parsed_osm = parsing_output[0]

bounds = parsed_osm['bounds']
way = parsed_osm['way']
node = parsed_osm['node']
relation = parsed_osm['relation']

ways_num = len(way['id'])
ways_node_set = way['nodes']
node_ids = dict()
n = len(node['id'])
for i in range(n):
    node_ids[node['id'][i]] = i

road_vals = ['highway', 'motorway', 'motorway_link', 'trunk', 'trunk_link',
             'primary', 'primary_link', 'secondary', 'secondary_link',
             'tertiary', 'road', 'residential', 'living_street',
             'service', 'services', 'motorway_junction']

Nnodes = parsing_output[1]


def create_connectivity():
        connectivity_matrix = np.full((Nnodes, Nnodes), float('inf'))
        np.fill_diagonal(connectivity_matrix, 0)

        for currentWay in range(ways_num):
            skip = True
            for i in way['tags'][currentWay]:
                if i['@k'] in road_vals:
                    skip = False
                    break
            if skip:
                continue

            nodeset = ways_node_set[currentWay]
            nodes_num = len(nodeset)

            currentWayID = way['id'][currentWay]

            for firstnode_local_index in range(nodes_num):
                firstnode_id = nodeset[firstnode_local_index]
                firstnode_index = node_ids.get(firstnode_id, -1)
                if firstnode_index == -1:
                    continue

                for othernode_local_index in range(firstnode_local_index+1, nodes_num):
                    othernode_id = nodeset[othernode_local_index]
                    othernode_index = node_ids.get(othernode_id, -1)
                    if othernode_index == -1:
                        continue

                    if (firstnode_id != othernode_id and connectivity_matrix[firstnode_index, othernode_index] == float('inf')):
                        connectivity_matrix[firstnode_index, othernode_index] = 1
                        connectivity_matrix[othernode_index, firstnode_index] = 1

        return connectivity_matrix

def dijkstra(start, end, connectivity_matrix):
    dist = [float('inf')] * len(connectivity_matrix)
    steps = [None] * len(connectivity_matrix)
    dist[start] = 0
    to_visit = set(range(len(connectivity_matrix)))

    while to_visit:
        current = min(to_visit, key=lambda vertex: dist[vertex])

        if dist[current] == float('inf'):
            break

        to_visit.remove(current)

        for neighbor in to_visit:
            if connectivity_matrix[current][neighbor] > 0:
                alt = dist[current] + connectivity_matrix[current][neighbor]
                if alt < dist[neighbor]:
                    dist[neighbor] = alt
                    # Update the path to the neighbor
                    if steps[current] is None:
                        steps[neighbor] = [start, neighbor]
                    else:
                        steps[neighbor] = steps[current] + [neighbor]

    return steps

print("Wait while the map is being generated...")

# Generating a map to display all the nodes
def BuildAllNodesMap():
    x1, y1 = (float(bounds[2]), float(bounds[0]))
    x2, y2 = (float(bounds[3]), float(bounds[1]))
    center = ((x1+x2)/2, (y1+y2)/2)
    map_0 = folium.Map(location=center, zoom_start=16)

    for i in range(n):
        xy = (node['xy'][i][0], node['xy'][i][1])
        folium.CircleMarker(xy, radius=3, color="green", fill=True,
                            fill_color="green", popup=str(i)).add_to(map_0)
    return map_0

# Generating a map to display all the nodes connected to the source
def BuildAllClosestNodesMap(SourceNode, nodes_routes_values):
    x1, y1 = (float(bounds[2]), float(bounds[0]))
    x2, y2 = (float(bounds[3]), float(bounds[1]))
    center = ((x1+x2)/2, (y1+y2)/2)
    map_0 = folium.Map(location=center, zoom_start=16)

    for i, j in nodes_routes_values:
        xy = (node['xy'][i][0], node['xy'][i][1])
        if (i != SourceNode):
            folium.CircleMarker(xy, radius=3, color="red", fill=True,
                                fill_color="green", popup=str(i)).add_to(map_0)
        else:
            folium.CircleMarker(xy, radius=3, color="blue", fill=True,
                                fill_color="green", popup=str(i)).add_to(map_0)
    return map_0

# Generating a map to display the path between source and destination
def BuildFinalPathMap(path):
    print(path)
    node_cds = [(node['xy'][path[0]][0], node['xy'][path[0]][1])]
    for i in range(1, len(path)):
        node_cds.append((node['xy'][path[i]][0], node['xy'][path[i]][1]))

    map_0 = folium.Map(location=node_cds[-1], zoom_start=15)

    folium.CircleMarker(node_cds[-1], radius=5, color="blue",
                        fill=True, fill_color="orange").add_to(map_0)
    folium.Marker(node_cds[0], icon=folium.Icon(
        color="blue", icon="circle", prefix='fa')).add_to(map_0)

    folium.PolyLine(locations=node_cds, weight=5, color="blue",
                    opacity="0.75", dash_array=10).add_to(map_0)

    return map_0

# Function to open a html file in browser
def OpenHTMLMapinBrowser(filename):
    url = "file://" + os.path.realpath(filename)
    webbrowser.open(url, new=2)

def main():
    # First Map Generator to show all the Nodes
    map1 = BuildAllNodesMap()
    map1.save("AllNodeMap.html")
    OpenHTMLMapinBrowser("AllNodeMap.html")

    # Third Map Generator to show path from source to destination
    while (True):
        SourceNode = int(input("Enter a source Node or 0 to exit:"))
        connectivity_matrix = create_connectivity()

        if (not SourceNode):
            print("Map Ended")
            sys.exit(1)

        while (True):
            DestinationNode = int(input(
                "Enter the selected Destination Node from the map or -1 to select a new node or 0 to exit :"))

            if (DestinationNode == -1):
                break

            if (not DestinationNode):
                print("Map Ended")
                sys.exit(1)

            path = dijkstra(SourceNode, DestinationNode, connectivity_matrix)
            print(path[DestinationNode])

            if path is None:
                print("No possible path between source and destination nodes")
                continue
            

            map3 = BuildFinalPathMap(path[DestinationNode])
            map3.save("OutputMap.html")
            OpenHTMLMapinBrowser("OutputMap.html")

main()