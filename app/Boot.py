import os, sys

sys.path.append(os.path.join(os.environ.get("SUMO_HOME"), "tools"))

from app.logging import info
from app.routing.CustomRouter import CustomRouter
from app.network.Network import Network
from app.simulation.Simulation import Simulation
from colorama import Fore
from sumo import SUMOConnector, SUMODependency
import Config
import traci, sys
import random

#for logging
from datetime import datetime
import csv


def start(processID, parallelMode,useGUI):

    random.seed(Config.random_seed)

    """ main entry point into the application """
    Config.parallelMode = parallelMode
    Config.sumoUseGUI = useGUI

    info('#####################################', Fore.CYAN)
    info('#        Starting TRAPP v0.1        #', Fore.CYAN)
    info('#####################################', Fore.CYAN)

    # Check if sumo is installed and available
    SUMODependency.checkDeps()
    info('# SUMO-Dependency check OK!', Fore.GREEN)

    # Load the sumo map we are using into Python
    Network.loadNetwork()
    info(Fore.GREEN + "# Map loading OK! " + Fore.RESET)
    info(Fore.CYAN + "# Nodes: " + str(Network.nodesCount()) + " / Edges: " + str(Network.edgesCount()) + Fore.RESET)

    # After the network is loaded, we init the router
    CustomRouter.init()
    # Start sumo in the background
    SUMOConnector.start()
    info("\n# SUMO-Application started OK!", Fore.GREEN)
    # Start the simulation
    Simulation.start()
    # Simulation ended, so we shutdown
    info(Fore.RED + '# Shutdown' + Fore.RESET)
    traci.close()
    sys.stdout.flush()
    return None


def start_multiple(processID, parallelMode,useGUI):
    def run_single():

        random.seed(Config.random_seed)
        
        # Start sumo in the background
        SUMOConnector.start()
        info("\n# SUMO-Application started OK!", Fore.GREEN)
        #create curstom router for simulation
        cr = CustomRouter()
        # create simulation object
        s = Simulation(cr)
        # Start the simulation
        avg_ovh = s.start()
        print avg_ovh
        # Simulation ended, so we shutdown
        traci.close()
        return avg_ovh

    """ main entry point into the application """
    Config.parallelMode = parallelMode
    Config.sumoUseGUI = useGUI

    info('#####################################', Fore.CYAN)
    info('#        Starting TRAPP v0.1        #', Fore.CYAN)
    info('#####################################', Fore.CYAN)
    
    # Check if sumo is installed and available
    SUMODependency.checkDeps()
    info('# SUMO-Dependency check OK!', Fore.GREEN)

    # Load the sumo map we are using into Python
    Network.loadNetwork()
    info(Fore.GREEN + "# Map loading OK! " + Fore.RESET)
    info(Fore.CYAN + "# Nodes: " + str(Network.nodesCount()) + " / Edges: " + str(Network.edgesCount()) + Fore.RESET)
        
    ## open file for logging
    filename = "average_overhead_"+str(datetime.now())+".csv"
    csvfile = open(filename,'w')
    fieldnames = ['sim_number', 'avgTripOverhead']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # loop for repeated simulations    
    for i in range(0, Config.num_sims):
        info(Fore.RED + '\n # Running simulation number '+ str(i+1) +'\n' + Fore.RESET)
        adpt_performance = run_single()
        writer.writerow({'sim_number': str(i), 'avgTripOverhead': adpt_performance})


    info("\n# finished simulations", Fore.GREEN)
    info(Fore.RED + '# Shutdown' + Fore.RESET)

    sys.stdout.flush()
    return None




    
