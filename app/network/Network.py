import sumolib

from app import Config
from app.routing.RoutingEdge import RoutingEdge

import os, sys

# used for random roadworks
import random

# import of SUMO_HOME
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class Network(object):
    """ simply ready the network in its raw form and creates a router on this network """
    
    # BAD FIX:  class variable that stores latest generated network object
    # this makes it impossible to parallelize simulations
    current_network = None

    # empty references to start with
    def __init__(self):

        self.edges = None
        self.nodes = None
        self.nodeIds = None
        self.edgeIds = None
        self.passenger_edges = None
        self.routingEdges = None

    def loadNetwork(self):
        """ loads the network and applies the results to the Network static class """
        # parse the net using sumolib
        parsedNetwork = sumolib.net.readNet(Config.sumoNet)
        # apply parsing to the network
        self.__applyNetwork(parsedNetwork)

    def __applyNetwork(self, net):
        Network.current_network = self #BAD FIX PART 2
        """ internal method for applying the values of a SUMO map """
        self.nodeIds = map(lambda x: x.getID(), net.getNodes())  # type: list[str]
        self.edgeIds = map(lambda x: x.getID(), net.getEdges(withInternal=False))  # type: list[str]
        self.nodes = net.getNodes()
        self.edges = net.getEdges(withInternal=False)
        self.passenger_edges = [e for e in net.getEdges(withInternal=False) if e.allows("passenger")]
        self.routingEdges = map(lambda x: RoutingEdge(x), self.passenger_edges)

    def nodesCount(self):
        """ count the nodes """
        return len(self.nodes)

    def edgesCount(self):
        """ count the edges """
        return len(self.edges)

    def getEdgeFromNode(self, edge):
        return edge.getFromNode()

    def getEdgeByID(self, edgeID):
        return [x for x in self.edges if x.getID() == edgeID][0]

    def getEdgeIDsToNode(self, edgeID):
        return self.getEdgeByID(edgeID).getToNode()

    # returns the edge position of an edge
    def getPositionOfEdge(self, edge):
        return edge.getFromNode().getCoord()  # @todo average two

    def get_random_node_id_of_passenger_edge(self, random):
        edge = random.choice(self.passenger_edges)
        return edge.getFromNode().getID()
