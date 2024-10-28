import osmnx as ox
import networkx as nx
from staticmap import StaticMap, Line
import pickle
import csv
import urllib
import haversine
import collections
import sklearn

Highway = collections.namedtuple('Highway', 'way_id description coordinates')  # Tram
Congestion = collections.namedtuple(
    'Congestion', 'congestion_id data current_status predicted_status')


def exists_graph(GRAPH_FILENAME):
    """ This boolean function returns if the graph is already downloaded
        with a certain filename. It tries to open it.

                    Time complexity: O(1). """

    try:
        file = open(GRAPH_FILENAME, 'rb')
        return True
    except:
        return False


def download_graph(PLACE):
    """ This function returns the undirected graph from a certain place.

        Precondition:
            1- The parameter given is a place that osmnx can handle.

                    Time complexity: O(1). """

    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    return graph


def save_graph(graph, GRAPH_FILENAME):
    """ This function saves the graph with the pickle module so it can be accessed at anytime.

                    Time complexity: O(1). """

    with open(GRAPH_FILENAME, 'wb') as file:
        pickle.dump(graph, file)


def load_graph(GRAPH_FILENAME):
    """ This function returns the graph we previously stored.

        Precondition:
            1- There must be a graph saved with this file name.

                    Time complexity: O(1). """

    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pickle.load(file)
        return graph


def plot_graph(graph):
    """ This function saves an image of the graph. It is a map of the city
        of Barcelona (in our case) with the edges (streets) and (intersections) highlighted.
        This option has been chosen due to practical uses and OS limitations.

        Precondition:
            1- The parameter given must be a proper osmnx undirected graph.

                    Time complexity: O(1). """

    ox.plot_graph(graph, show=False, save=True, filepath='barcelona.png')


def download_highways(HIGHWAYS_URL):
    """ Using the urllib library, this function downloads the highways data. It returns
        a list containing information of each of Barcelona's highways.

        Precondition:
            1- The file must contain data regarding highways in the city.
            2- The data must be stored in a .csv file.

                    Time complexity: O(lines). """

    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        highways = list()
        for line in reader:
            way_id, description, coordinates = line
            coordinates = coordinates.split(',')
            highways.append(Highway(int(way_id), description,
                                    [float(coord) for coord in coordinates]))
        return highways


def plot_highways(highways, highways_file, SIZE):
    """ This function saves an image of our city(with the name of the file and the size given)
        with just the highways highlighted.

        Preconditions:
            1- highways must be a proper list of the city's highways information.
            2- highways_file must be in a correct format

                    Time complexity: O(highways.size*max(highways.coordinates.size)). """

    map = StaticMap(SIZE, SIZE)
    for highway in highways:
        it = 0
        while(it < len(highway.coordinates) - 3):
            map.add_line(Line(((highway.coordinates[it], highway.coordinates[it+1]),
                               (highway.coordinates[it+2], highway.coordinates[it+3])), 'blue', 3))
            it += 2
    image = map.render()
    image.save(highways_file)


def download_congestions(CONGESTIONS_URL):
    """ Using the urllib library it downloads the congestions data. This function returns a
        list containing information of the congestions data in some highways.

        Precondition:
            1- The file must contain data regarding congestions in the city.
            2- The data must be stored in a .csv file.

            Time complexity: O(lines). """

    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')
        next(reader)  # ignore first line with description
        congestions = list()
        for line in reader:
            congestion_id, data, current_status, predicted_status = line
            congestions.append(Congestion(int(congestion_id), int(
                data), int(current_status), int(predicted_status)))
        return congestions


def plot_congestions(highways, congestions, congestions_file, SIZE):
    """ It saves an image of our city(with the name of the file and the size given)
        with just the highways colored depending on their congestion status.

        Preconditions:
            1- A list of highways and a list of congestions(with their corresponding information) are given.
            2- congestions_file must be in a correct format

                    Time complexity: O(highways.size*congestions.size) """

    map = StaticMap(SIZE, SIZE)
    for highway in highways:
        highway_status = search_congestion_status(highway.way_id, congestions)
        color = conversion(highway_status)
        it = 0
        while(it < len(highway.coordinates) - 3):
            map.add_line(Line(((highway.coordinates[it], highway.coordinates[it+1]),
                               (highway.coordinates[it+2], highway.coordinates[it+3])), color, 3))
            it += 2
    image = map.render()
    image.save(congestions_file)


def conversion(current_status):
    """ This function returns the type of congestion given a number(that represents the status).

        Preconditions:
            1- The parameter given mast be bounded [0,6]

                    Time complexity: O(1). """

    if current_status == 0:  # no information of the congestion
        return 'grey'
    if current_status == 1:  # very fluid
        return 'green'
    if current_status == 2:  # fluid
        return 'orange'
    if current_status == 3:  # dense
        return 'yellow'
    if current_status == 4:  # very dense
        return 'brown'
    if current_status == 5:  # congestion
        return 'red'
    if current_status == 6:  # closed
        return 'black'


def search_congestion_status(way_id, congestions):
    """ This function searches in the congestions file the status from a certain
        highway comparing its id. It returns the highway congestion (0 if no
        information has been found).

        Preconditions:
            1- congestions must be a proper list with the congestions information.

                    Time complexity: O(congestions.size). """

    for congestion in congestions:
        if congestion.congestion_id == way_id:
            return congestion.current_status
    return 0


def has_maxspeed(edge):
    """Boolean function that returns if a certain edge has the attribute: maxspeed.
        It tries to access it.


                    Time complexity: O(1)"""
    try:
        variable = edge['maxspeed']
        return True
    except:
        return False


def calculate_max_speed(type_of_street):
    """ Function that calculates the speed limit of an edge given its type. If
        there are various types(3 maximum), we choose the one with most speed limit.

        Preconditions:
            1- The parameter given must contain proper types of streets

                    Time complexity: O(1)"""

    if type(type_of_street) == list:
        list_of_maxspeeds = list()
        for street in type_of_street:
            list_of_maxspeeds.append(speed_limit(street))
        return max(list_of_maxspeeds)
    return speed_limit(type_of_street)


def speed_limit(street):
    """ Function that returns the speed limit of an edge depending on its type of street.

        Preconditions:
            1- The parameter given must contain a proper types of street

                Time complexity: O(1)"""

    if street == 'residential' or 'residential_link':
        return 30
    if street == 'living_sreet' or 'living_sreet_link':
        return 20
    if street == 'primary' or 'primary_link':
        return 50
    if street == 'secondary' or 'secondary_link':
        return 40
    if street == 'tertiary' or 'tertiary_link':
        return 30
    if street == 'trunk' or 'trunk_link':
        return 90


def max_of_list(list_of_velocities_str):
    """ This function returns the maximum speed limit of a list(of constant size) of speed limits
        in string format.

        Precondition:
            1- The list given must be in the correct format.

        Time complexity: O(1) """

    list_of_velocities_int = list()
    for velocity in list_of_velocities_str:
        list_of_velocities_int.append(int(velocity))
    return max(list_of_velocities_int)


def fill_all_maxspeeds(graph):
    """ This function assigns a maxspeed to all edges. We have three cases,
        if the edge has no maxspeed, if there is a list of maxspeeds
        and if there is only one maxspeed. It's important to notice that this
        attribute is initially of string class(so we have to convert it).

        Precondition:
            1- The parameter given must be in the correct format and have the correct attributes.

                    Time Complexity: O(edges)"""

    for node1, info1 in graph.nodes.items():
        for node2, edge in graph.adj[node1].items():
            if not has_maxspeed(edge):  # if the edge has no maxspeed
                edge['maxspeed'] = calculate_max_speed(edge['highway'])
            elif type(edge['maxspeed']) == list:
                edge['maxspeed'] = max_of_list(edge['maxspeed'])
            else:
                edge['maxspeed'] = int(edge['maxspeed'])


def propagate_congestion(graph, shortest_path, status):
    """ This function propagates congestion through the shortest path(list of nodes)

        Precondition: 1- graph must be directed and correct
                      2- shortest_path must be a list of nodes
                      3- status is bounded

        Time complexity: O(shortest_patg.size)"""
    if type(shortest_path) == list:
        it = 0
        while(it < len(shortest_path)-1):
            node1 = shortest_path[it]
            node2 = shortest_path[it+1]
            graph.adj[node1][node2]['congestion'] = int(status)
            it += 1


def propagate_congestion_for_all_edges(graph, highways, congestions):
    """ This function assigns to each edge their congestion status. To do so,
        this function propagates the congestion status of each highway through
        the shortest path between the nearest node of beginning of the highway
        the nearest node of the end of the highway.

       Preconditions:
            1 - The graph given must be a directed graph with appropiate edges attributes
            2 - highways and congestions must be in correct format

        Time complexity: O(highways*(congestions + nodes + edges*log(nodes))) =
                    = O(highways*edges*log(nodes))"""

    for highway in highways:
        status = search_congestion_status(highway.way_id, congestions)
        if status != 0:  # we already set all edges congestion to 0
            node_org = ox.distance.nearest_nodes(
                graph, highway.coordinates[0], highway.coordinates[1])
            node_dst = ox.distance.nearest_nodes(graph, highway.coordinates[len(
                highway.coordinates)-2], highway.coordinates[len(highway.coordinates) - 1])
            shortest_path = ox.shortest_path(graph, node_org, node_dst)
            propagate_congestion(graph, shortest_path, status)


def calculate_itime(congestion, length, max_speed):
    """ This function calculates the itime of a given edge. The idea is that
        the max speed will be scaled in proportion to the level of congestion in
        that edge. However if we don't know the congestion, we will suppose there is
        intermidiate congestion and if the street is closed the itime will be set
        to infinite(for dijkstra properties).

        Preconditions:
            1- congestions is bounded between [0, 6].
            2- max_speed and length is given properly.

                    Time complexity: 0(1) """

    if congestion != 0 and congestion != 6:
        return max_speed - ((max_speed/5) * (congestion-1))
    elif congestion == 0:
        return max_speed/2
    else:
        return float('inf')


def calculate_i_time_for_all_edges(graph):
    """ This function propagates the time to travel through an edge through
        all of them.

        Precondition:
            1- graph must be a defined graph with proper edge attributes.

        Time complexity: O(edges) """

    for node1, info1 in graph.nodes.items():
        for node2, edge in graph.adj[node1].items():
            new_time = calculate_itime(edge['congestion'], edge['length'], edge['maxspeed'])
            edge['itime'] = new_time


def build_igraph(graph, highways, congestions):
    """ This function returns the iGraph, an advanced graph that takes into account
        the highway congestions. The edges of this graph will have two new attributes,
        the congestion status(congestion) and the time(itime) to travel through the edge.

        Preconditions:
            1- We must get a defined graph.
            2- We must get a proper list of highways.
            3- We must get a proper list of congestions.

        Time complexity: O(edges) + O(highways*(congestions + nodes + edges*log(nodes)))
                    = O(highways*edges*log(nodes)) as it's a sparse graph"""

    graph = ox.utils_graph.get_digraph(graph, weight='length')
    fill_all_maxspeeds(graph)
    nx.set_edge_attributes(graph, 0, "congestion")
    nx.set_edge_attributes(graph, None, "itime")
    propagate_congestion_for_all_edges(graph, highways, congestions)
    calculate_i_time_for_all_edges(graph)
    return graph


def get_shortest_path_with_ispeeds(igraph, orig, dst):
    """ This function returns the sortest path(list of nodes) between two places
        (orig and dst). This path will be calculated in relation to the attribute
        itime.

        Preconditions:
            1- origin and destination must be valid places.
            2- igraph must be defined(and with the proper edge attributes).

                Time complexity: O(nodes) + O(edges*log(nodes))=
                            = O(edges*log(nodes)).  """

    orig_long, orig_lat = ox.geocoder.geocode(orig + ', Barcelona')
    dst_long, dst_lat = ox.geocoder.geocode(dst + ', Barcelona')
    return get_shortest_path_between_coords(igraph, orig_long, orig_lat, dst_long, dst_lat)


def get_shortest_path_between_coords(igraph, orig_long, orig_lat, dst_long, dst_lat):
    """ This function is basically implemented for bot issues, it returns the shortest path
        between two coordinates.

        Preconditions: 1- igraph must be defined and directed
                       2- the second group of parameters(coords) must be valid """

    node_orig = ox.distance.nearest_nodes(igraph, orig_lat, orig_long)
    node_dst = ox.distance.nearest_nodes(igraph, dst_lat, dst_long)
    return ox.shortest_path(igraph, node_orig, node_dst, weight='itime')


def plot_path(igraph, ipath, SIZE):
    """ This funtion saves an image of the shortest path(with colored highways
        depending on the congestion) between origin and destination in a representation
        of the city.

        Preconditions:
            1 - igraph must be defined(and with the proper attributes)

                    Time complexity: O(ipath.size) """

    map = StaticMap(SIZE, SIZE)
    it = 0
    if type(ipath) == list:
        while it < len(ipath) - 1:
            node1 = ipath[it]
            node2 = ipath[it+1]
            map.add_line(Line(((igraph.nodes[node1]['x'], igraph.nodes[node1]['y']),
                               (igraph.nodes[node2]['x'], igraph.nodes[node2]['y'])),
                              conversion(igraph.adj[node1][node2]['congestion']), 5))
            it += 1
        image = map.render()
        image.save('shortest_path.png')
    else:
        print("No path found")
