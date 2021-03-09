import subprocess
from app import Config
import fileinput
import sys, os
from app.network.Network import Network

from app.entity.Car import Car
from app.Util import  prepare_epos_input_data_folders
from app.Util import get_output_folder_for_latest_EPOS_run
from app.adaptation import Knowledge

class NullCar:
    """ a car with no function used for error prevention """
    def __init__(self):
        pass

    def setArrived(self, tick):
        pass


class CarRegistry(object):
    """ central registry for all our cars we have in the sumo simulation """

    def __init__(self):
        self.vehicle_length = 5
        # the total amount of cars that should be in the system
        self.totalCarCounter = Config.totalCarCounter
        # always increasing counter for carIDs
        self.carIndexCounter = 0
        # list of all cars
        self.cars = {}  # type: dict[str,app.entitiy.Car]
        # counts the number of finished trips
        self.totalTrips = 0
        # average of all trip durations
        self.totalTripAverage = 0
        # average of all trip overheads (overhead is TotalTicks/PredictedTicks)
        self.totalTripOverheadAverage = 0

    # @todo on shortest path possible -> minimal value

    def applyCarCounter(self):
        """ syncs the value of the carCounter to the SUMO simulation """
        while len(self.cars) < self.totalCarCounter:
            # to less cars -> add new
            c = Car("car-" + str(self.carIndexCounter),self)
            self.carIndexCounter += 1
            self.cars[c.id] = c
            c.addToSimulation(0, True)
        while len(self.cars) > self.totalCarCounter:
            # to many cars -> remove cars
            (k, v) = self.cars.popitem()
            v.remove()

    def findById(self, carID):
        """ returns a car by a given carID """
        try:
            return self.cars[carID]  # type: app.entitiy.Car
        except:
            return NullCar()

    def do_epos_planning(self, tick):
        prepare_epos_input_data_folders()

        cars_to_indexes = {}
        i = 0
        for car_id, car in self.cars.iteritems():
            if car.create_epos_output_files_based_on_current_location(tick, str(i)):
                cars_to_indexes[car_id] = i
                i += 1

        number_of_epos_plans = len([name for name in os.listdir('datasets/plans') if name.endswith("plans")])
        print "Number of EPOS plans: " + str(number_of_epos_plans)

        Knowledge.time_of_last_EPOS_invocation = tick
        
        self.change_EPOS_config("conf/epos.properties", "numAgents=", "numAgents=" + str(number_of_epos_plans))
        self.change_EPOS_config("conf/epos.properties", "planDim=", "planDim=" + str(Network.edgesCount() * Knowledge.planning_steps))
        self.change_EPOS_config("conf/epos.properties", "alpha=", "alpha=" + str(Knowledge.alpha))
        self.change_EPOS_config("conf/epos.properties", "beta=", "beta=" + str(Knowledge.beta))
        self.change_EPOS_config("conf/epos.properties", "globalCostFunction=", "globalCostFunction=" + str(Knowledge.globalCostFunction))

        self.run_epos_apply_results(False, cars_to_indexes, tick)

    def run_epos_apply_results(self, first_invocation, cars_to_indexes, tick):
        p = subprocess.Popen(["java", "-jar", Config.epos_jar_path])
        print "Invoking EPOS at tick " + str(tick)
        p.communicate()
        print "EPOS run completed!"
        self.selectOptimalRoutes(get_output_folder_for_latest_EPOS_run(), first_invocation, cars_to_indexes)

    def selectOptimalRoutes(self, output_folder_for_latest_run, first_invocation, cars_to_indexes):

        with open(output_folder_for_latest_run + '/selected-plans.csv', 'r') as results:
            line_id = 1
            for line in results:
                if line_id == 41:
                    res = [int(x) for x in line.split(",")[2:]]
                    break
                line_id += 1

        i = 0
        for car_id, epos_id in cars_to_indexes.iteritems():
            c = self.cars[car_id]
            with open('datasets/routes/agent_' + str(epos_id) + '.routes', 'r') as plans_file:
                plans=plans_file.readlines()
            if Config.debug:
                print "attempting to change the route of " + str(c.id)
            selected_route = plans[res[epos_id]].replace('\r', '').replace('\n', '').split(",")
            i += 1

            previous_preference = c.driver_preference
            previous_route = c.currentRouterResult.route
            c.change_route(selected_route, first_invocation)
            c.change_preference(res[epos_id])
            current_preference = c.driver_preference
            current_route = c.currentRouterResult.route
            if Config.debug:
                if previous_preference == current_preference:
                    print "preference did not change: " + str(previous_preference)
                else:
                    print "preference changed. Old preference: " + str(previous_preference) + ", New preference: " + str(current_preference)
                if set(current_route) <= set(previous_route):
                    print "route did not change"
                else:
                    print "route changed"

    def change_EPOS_config(self, filename, searchExp, replaceExp):
        for line in fileinput.input(filename, inplace=True):
            if searchExp in line:
                line = replaceExp + "\n"
            sys.stdout.write(line)