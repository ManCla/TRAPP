from random import gauss

from dijkstar import Graph, find_path

from app.network.Network import Network
from app.routing.RouterResult import RouterResult


class CustomRouter(object):
    """ our own custom defined router """

    def __init__(self):
            # Empty starting references
        self.edgeMap = None
        self.graph = None

        # the percentage of smart cars that should be used for exploration
        self.explorationPercentage = 0.0 # INITIAL JSON DEFINED!!!
        # randomizes the routes
        self.routeRandomSigma = 0.2 # INITIAL JSON DEFINED!!!
        # how much speed influences the routing
        self.maxSpeedAndLengthFactor = 1 # INITIAL JSON DEFINED!!!
        # multiplies the average edge value
        self.averageEdgeDurationFactor = 1 # INITIAL JSON DEFINED!!!
        # how important it is to get new data
        self.freshnessUpdateFactor = 10 # INITIAL JSON DEFINED!!!
        # defines what is the oldest value that is still a valid information
        self.freshnessCutOffValue = 500.0 # INITIAL JSON DEFINED!!!
        # how often we reroute cars
        self.reRouteEveryTicks = 20 # INITIAL JSON DEFINED!!!
        """ set up the router using the already loaded network """
        self.graph = Graph()
        self.edgeMap = {}
        for edge in Network.routingEdges:
            self.edgeMap[edge.id] = edge
            self.graph.add_edge(edge.fromNodeID, edge.toNodeID,
                                {'length': edge.length, 'maxSpeed': edge.maxSpeed,
                                 'lanes': len(edge.lanes), 'edgeID': edge.id})

    def minimalRoute(self, fr, to):
        """creates a minimal route based on length / speed  """
        cost_func = lambda u, v, e, prev_e: e['length'] / e['maxSpeed']
        route = find_path(self.graph, fr, to, cost_func=cost_func)
        return RouterResult(route, False)

    def route(self, fr, to, tick, car):
        """ creates a route from the f(node) to the t(node) """
        # 1) SIMPLE COST FUNCTION
        # cost_func = lambda u, v, e, prev_e: max(0,gauss(1, CustomRouter.routeRandomSigma) \
        #                                         * (e['length']) / (e['maxSpeed']))

        # if car.victim:
        #     # here we reduce the cost of an edge based on how old our information is
        #     print("victim routing!")
        #     cost_func = lambda u, v, e, prev_e: (
        #         self.getAverageEdgeDuration(e["edgeID"]) -
        #         (tick - (self.edgeMap[e["edgeID"]].lastDurationUpdateTick))
        #     )
        # else:
        # 2) Advanced cost function that combines duration with averaging
        # isVictim = ??? random x percent (how many % routes have been victomized before)

        # isVictim = self.explorationPercentage > random()
        isVictim = False

        if isVictim:
            victimizationChoice = 1
        else:
            victimizationChoice = 0

        cost_func = lambda u, v, e, prev_e: \
            self.getFreshness(e["edgeID"], tick) * \
            self.averageEdgeDurationFactor * \
            self.getAverageEdgeDuration(e["edgeID"]) \
            + \
            (1 - self.getFreshness(e["edgeID"], tick)) * \
            self.maxSpeedAndLengthFactor * \
            max(1, gauss(1, self.routeRandomSigma) *
            (e['length']) / e['maxSpeed']) \
            - \
            (1 - self.getFreshness(e["edgeID"], tick)) * \
            self.freshnessUpdateFactor * \
            victimizationChoice

        # generate route
        route = find_path(self.graph, fr, to, cost_func=cost_func)
        # wrap the route in a result object
        return RouterResult(route, isVictim)

    def getFreshness(self, edgeID, tick):
        try:
            lastUpdate = float(tick) - self.edgeMap[edgeID].lastDurationUpdateTick
            return 1 - min(1, max(0, lastUpdate / self.freshnessCutOffValue))
        except TypeError as e:
            # print("error in getFreshnessFactor" + str(e))
            return 1

    def getAverageEdgeDuration(self, edgeID):
        """ returns the average duration for this edge in the simulation """
        try:
            return self.edgeMap[edgeID].averageDuration
        except:
            print("error in getAverageEdgeDuration")
            return 1

    def applyEdgeDurationToAverage(self, edge, duration, tick):
        """ tries to calculate how long it will take for a single edge """
        try:
            self.edgeMap[edge].applyEdgeDurationToAverage(duration, tick)
        except:
            return 1

    def route_by_max_speed(self, fr, to):
        """ creates a route from the f(node) to the t(node) """
        cost_func = lambda u, v, e, prev_e: (1 / e['maxSpeed'])
        route = find_path(self.graph, fr, to, cost_func=cost_func)
        return RouterResult(route, False)

    def route_by_min_length(self, fr, to):
        """ creates a route from the f(node) to the t(node) """
        cost_func = lambda u, v, e, prev_e: (e['length'])
        route = find_path(self.graph, fr, to, cost_func=cost_func)
        return RouterResult(route, False)

    def calculate_length_of_route(self, route):
        return sum([self.edgeMap[e].length for e in route])
