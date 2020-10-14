pip install simpy

python carwash.py -r 42 -m 2 -w 5 -t 7 -s 20


Check the variables:

-r RANDOM_SEED = 42
-m NUM_MACHINES (= 2 # Number of machines in the carwash
-w WASHTIME = 5 # Minutes it takes to clean a car
-t T_INTER = 7 # Create a car every ~7 minutes
-s SIM_TIME = 20 # Simulation time in minutes
 

-r (for random seed),

-m (for number of machines),

-w (for minutes to wash),

-t (for interval that cars are generated), and

-s (for simulation time in minutes)



OUTPUT:
Graphs of:
	How long cars wait on car washes
Depending on paramters:
Plot it over time, use multiple parameters (e.g., different number of washers, in a single plot). Please analyze (at least the length of the line over time, if you are analyzing both wait time and car line length you will earn bonus points.