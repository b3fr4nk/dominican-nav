import xmltodict as xtd

def parseOSM(path):
    # open file
    with open(path, "rb") as osm_fn:
        map_osm = xtd.parse(osm_fn)['osm']


    # Parsing bounds from .OSM file
    ymax = map_osm['bounds']['@maxlat']
    ymin = map_osm['bounds']['@minlat']
    xmax = map_osm['bounds']['@maxlon']
    xmin = map_osm['bounds']['@minlon']
    parsed_bounds = [xmin, xmax, ymin, ymax]

    # Parsing Node
    Node = map_osm['node']
    Nnodes = len(Node)
    Nodeid = [0]*Nnodes
    xy = []
    for i in range(Nnodes):
        Nodeid[i] = float(Node[i]['@id'])
        x = float(Node[i]['@lat'])
        y = float(Node[i]['@lon'])
        xy.append([x, y])
    parsed_node = {'id': Nodeid, 'xy': xy}

    # Parsing Ways
    Way = map_osm['way']
    Nways = len(Way)
    Wayid = [0]*Nways
    nodes_in_way = [0]*Nways
    tags = [0]*Nways
    for i in range(Nways):
        tempWay = Way[i]
        Wayid[i] = float(tempWay['@id'])
        Nnd = len(tempWay['nd'])
        ndTemp = [0]*Nnd
        for j in range(Nnd):
            ndTemp[j] = float(tempWay['nd'][j]['@ref'])
        nodes_in_way[i] = ndTemp
        if 'tag' in tempWay.keys():
            if type(tempWay['tag']) is list:
                tags[i] = tempWay['tag']
            else:
                tags[i] = [tempWay['tag']]
        else:
            tags[i] = []
    parsed_way = {'id': Wayid, 'nodes': nodes_in_way, 'tags': tags}

    # Parsing Relations
    Relation = map_osm['relation']
    Nrelation = len(Relation)
    Relationid = [0]*Nrelation
    for i in range(Nrelation):
        currentRelation = Relation[i]
        currentId = currentRelation['@id']
        Relationid[i] = float(currentId)
    parsed_relation = {'id': Relationid}

    # Parsing .OSM file
    parsed_osm = {
        'bounds': parsed_bounds,
        'relation': parsed_relation,
        'way': parsed_way,
        'node': parsed_node,
        'attributes': map_osm.keys()
    }

    return (parsed_osm, Nnodes)
