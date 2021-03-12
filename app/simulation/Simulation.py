import json
import traci
import traci.constants as tc

from colorama import Fore

from app import Config
from app.entity.CarRegistry import CarRegistry
from app.logging import info
import time

from app.logging import CSVLogger

import app.Util as Util
from app.adaptation import perform_adaptation
from app.adaptation import Knowledge

current_milli_time = lambda: int(round(time.time() * 1000))


class Simulation(object):
    """ here we run the simulation in """

    # the current tick of the simulation
    tick = 0

    # last tick time
    lastTick = current_milli_time()

    def __init__(self, cstmrtr, ntw):
        self.cr = cstmrtr   # custom router object of this simulaiton
        self.network = ntw  # Network object of this simulation

    def applyFileConfig(self):
        """ reads configs from a json and applies it at realtime to the simulation """
        try:
            config = json.load(open('./knobs.json'))
            cr.explorationPercentage = config['explorationPercentage']
            cr.averageEdgeDurationFactor = config['averageEdgeDurationFactor']
            cr.maxSpeedAndLengthFactor = config['maxSpeedAndLengthFactor']
            cr.freshnessUpdateFactor = config['freshnessUpdateFactor']
            cr.freshnessCutOffValue = config['freshnessCutOffValue']
            cr.reRouteEveryTicks = config['reRouteEveryTicks']
        except:
            pass

    def start(self):

        Knowledge.planning_period = Config.planning_period
        Knowledge.planning_step_horizon = Config.planning_step_horizon
        Knowledge.planning_steps = Config.planning_steps
        Knowledge.alpha = Config.alpha
        Knowledge.beta = Config.beta
        Knowledge.globalCostFunction = Config.globalCostFunction

        Util.remove_overhead_and_streets_files()
        Util.add_data_folder_if_missing()

        CSVLogger.logEvent("streets", [edge.id for edge in self.network.routingEdges])

        Util.prepare_epos_input_data_folders()

        """ start the simulation """

        self.carreg = CarRegistry(self.network)
        info("# Start adding initial cars to the simulation", Fore.MAGENTA)
        # apply the configuration from the json file
        self.applyFileConfig()
        self.carreg.applyCarCounter(self.cr)

        if Config.start_with_epos_optimization:
            Knowledge.time_of_last_EPOS_invocation = 0
            self.carreg.change_EPOS_config("conf/epos.properties", "numAgents=", "numAgents=" + str(Config.totalCarCounter))
            self.carreg.change_EPOS_config("conf/epos.properties", "planDim=", "planDim=" + str(self.network.edgesCount() * Knowledge.planning_steps))
            self.carreg.change_EPOS_config("conf/epos.properties", "alpha=", "alpha=" + str(Knowledge.alpha))
            self.carreg.change_EPOS_config("conf/epos.properties", "beta=", "beta=" + str(Knowledge.beta))
            self.carreg.change_EPOS_config("conf/epos.properties", "globalCostFunction=", "globalCostFunction=" + str(Knowledge.globalCostFunction))

            cars_to_indexes = {}
            for i in range(Config.totalCarCounter):
                cars_to_indexes["car-" + str(i)] = i
            self.carreg.run_epos_apply_results(True, cars_to_indexes, 0)

        return self.loop()

    # @profile
    def loop(self):
        """ loops the simulation """

        # start listening to all cars that arrived at their target
        traci.simulation.subscribe((tc.VAR_ARRIVED_VEHICLES_IDS,))
        while 1:

            if len(self.carreg.cars) == 0:
                print("all cars reached their destinations")
                return

            # Do one simulation step
            self.tick += 1
            traci.simulationStep()

            # Check for removed cars and re-add them into the system
            for removedCarId in traci.simulation.getSubscriptionResults()[122]:
                if Config.debug:
                    print str(removedCarId) + "\treached its destination at tick " + str(self.tick)
                self.carreg.findById(removedCarId).setArrived(self.tick)

            CSVLogger.logEvent("streets", [self.tick] + [traci.edge.getLastStepVehicleNumber(edge.id)*self.carreg.vehicle_length / edge.length for edge in self.network.routingEdges])

            if (self.tick % 50) == 0:
                info("Simulation -> Step:" + str(self.tick) + " # Driving cars: " + str(
                    traci.vehicle.getIDCount()) + "/" + str(
                    self.carreg.totalCarCounter) + " # avgTripOverhead: " + str(
                    self.carreg.totalTripOverheadAverage), Fore.GREEN)

            if Config.simulation_horizon == self.tick:
                print("Simulation horizon reached!")
                return str(self.carreg.totalTripOverheadAverage)

            if (self.tick % Config.adaptation_period) == 0:
                perform_adaptation(self.tick)

            if (self.tick % Knowledge.planning_period) == 0:
                self.carreg.do_epos_planning(self.tick)

