######################################
####### GENERAL CONFIGURATION ########
######################################

# True if we want to use the SUMO GUI
sumoUseGUI = False

# True for printing extra info
debug = False

# which seed to be used in the random functions, for repeatability
random_seed = 1

num_sims = 300

# The path to EPOS jar that is called from Python for planning
# <path to EPOS jar>
epos_jar_path = "/Users/claudio/repositories-git/TRAPP/EPOS/release-0.0.1/epos-tutorial.jar"

######################################
#### CONFIGURATION OF SIMULATION #####
######################################

#### MAP ####

# The SUMO config (links to the network) we use for our simulation
# <path to SUMO cfg file>
sumoConfig = "/Users/claudio/repositories-git/TRAPP/app/map/eichstaedt.sumo.cfg"

# The SUMO network file we use for our simulation
# <path to SUMO net.xml file>
sumoNet = "/Users/claudio/repositories-git/TRAPP/app/map/eichstaedt.net.xml"

#### SIMULATION SETUP ####

# The total number of cars we use in our simulation
carsNumberBase  = 800
carsNumberRange = 400

# How long the simulation will run
simulation_horizon = 1000

######################################
##### CONFIGURATION OF PLANNING ######
######################################

# whether the simulation should start with an EPOS invocation
start_with_epos_optimization = False

#### initialization of control action of outer adaptive loop ####

# How frequently EPOS planning will be invoked (runtime-configurable parameter)
planning_period = 100

# the number of steps to look in the future while planning
planning_steps = 1

# how long a planning step should be
planning_step_horizon = 50

# double from [0, 1], unfairness
alpha = 0

# double from [0, 1], selfishness or local objective
beta = 1
# unfairness + selfishness <= 1
# alpha*unfairness + beta*local_cost + (1-alpha-beta)*global_costs

# Suggested values : "XCORR", VAR", "RSS", "RMSE"
globalCostFunction="RMSE"

######################################
#### CONFIGURATION OF ADAPTATION #####
######################################

# how often adaptation should be triggered
adaptation_period = 100

# the actual adaptation logic. Possible values: "load_balancing", "avoid_overloaded_streets", "tune_planning_resolution"
adaptation_strategy = "avoid_overloaded_streets"