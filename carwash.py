"""
Carwash example.

Covers:

- Waiting for other processes
- Resources: Resource

Scenario:
  A carwash has a limited number of washing machines and defines
  a washing processes that takes some (random) time.

  Car processes arrive at the carwash at a random time. If one washing
  machine is available, they start the washing process and wait for it
  to finish. If not, they wait until they an use one.

"""
import random
import simpy
import getopt
import sys
import pandas as pd
import matplotlib.pyplot  as plt
from scipy.stats import poisson
import math

argumentHash = {'RANDOM_SEED': -1, 'NUM_MACHINES': -1, 'WASHTIME': -1, 'T_INTER': -1, 'SIM_TIME': -1 }
otherDict = {'cars':[], 'arrives':[], 'enters':[], 'leaves':[], 'waitingTime': [] }
trackingDict = {}
pos = 0
class Carwash(object):
    """A carwash has a limited number of machines (``NUM_MACHINES``) to
    clean cars in parallel.

    Cars have to request one of the machines. When they got one, they
    can start the washing processes and wait for it to finish (which
    takes ``washtime`` minutes).

    """

    def __init__(self, env, num_machines, washtime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime

    def wash(self, car):
        """The washing processes. It takes a ``car`` processes and tries
        to clean it."""
        yield self.env.timeout(argumentHash['WASHTIME'])
        print("Carwash removed %d%% of %s's dirt." %
              (random.randint(50, 99), car))


def prossargs():
    try:
        opt, args = getopt.getopt(sys.argv[1:], "r:m:w:t:s:p:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opts, arg in opt:

        if not arg.isdigit():
            print('please input only int values for args')
            usage()
            exit(2)
        if opts == '-r':
            argumentHash['RANDOM_SEED'] = int(arg)
        elif opts == '-m':
            argumentHash['NUM_MACHINES'] = int(arg)
        elif opts == '-w':
            argumentHash['WASHTIME'] = int(arg)
        elif opts == '-t':
            argumentHash['T_INTER'] = int(arg)
        elif opts == '-s':
            argumentHash['SIM_TIME'] = int(arg)
        elif opts == '-p':
            global pos
            pos = 1
    for a in argumentHash.keys():
        if argumentHash[a] == -1:
            print("Cannot leave input  null")
            usage()
            exit(2)


def usage():
    print(
        "python carwash.py -r 'randomSeed`=' -m 'number of machines' -w 'minutes to wash' \-t 'interval cars generated' -s 'simtime in mins'")


def car(env, name, cw):
    """The car process (each car has a ``name``) arrives at the carwash
    (``cw``) and requests a cleaning machine.

    It then starts the washing process, waits for it to finish and
    leaves to never come back ...

    """
    print('%s arrives at the carwash at %.2f.' % (name, env.now))
    trackingDict[name] = [env.now]
    with cw.machine.request() as request:
        yield request

        print('%s enters the carwash at %.2f.' % (name, env.now))
        trackingDict[name].append(env.now)
        yield env.process(cw.wash(name))

        print('%s leaves the carwash at %.2f.' % (name, env.now))
        trackingDict[name].append(env.now)

def setup(env, num_machines, washtime, t_inter):
    """Create a carwash, a number of initial cars and keep creating cars
    approx. every ``t_inter`` minutes."""
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    # Create 4 initial cars
    for i in range(4):
        env.process(car(env, 'Car %d' % i, carwash))

    # Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        i += 1
        env.process(car(env, 'Car %d' % i, carwash))

def timeInterval():
    """

    :return: a list of times that can be used for plot
    """
    baseValue = math.floor(float(argumentHash['SIM_TIME']) / float(otherDict['cars'][-1][-1]))
    timeList = []
    value = 0
    for a in range(0, int(otherDict['cars'][-1][-1])+1):
        timeList.append(value)
        value += baseValue
    return timeList


# Setup and start the simulation
#print('Carwash')
#print('Check out http://youtu.be/fXXmeP9TvBg while simulating ... ;-)')
prossargs()
random.seed(argumentHash['RANDOM_SEED'])  # This helps reproducing the results

# Create an environment and start the setup process

for a in range(3):
    colors = ['b', 'c', 'm']
    otherDict = {'cars':[], 'arrives':[], 'enters':[], 'leaves':[], 'waitingTime': [] }
    env = simpy.Environment()
    if a == 0:
        env.process(setup(env, argumentHash['NUM_MACHINES'], argumentHash['WASHTIME'], argumentHash['T_INTER']))
        # Execute!
        env.run(until=int(argumentHash['SIM_TIME']))
    else:
        env.process(setup(env, int(argumentHash['NUM_MACHINES'])+a, argumentHash['WASHTIME'], argumentHash['T_INTER']))
        env.run(until=int(argumentHash['SIM_TIME']))
    for keys in trackingDict:
        otherDict['cars'].append(keys)

        if len(trackingDict[keys]) >= 1:
            otherDict['arrives'].append(trackingDict[keys][0])
        if len(trackingDict[keys]) >= 2:
            otherDict['enters'].append(trackingDict[keys][1])
            otherDict['waitingTime'].append(float(trackingDict[keys][1])-float(trackingDict[keys][0]))
        if len(trackingDict[keys]) >= 3:
            otherDict['leaves'].append(trackingDict[keys][2])
        else:
            otherDict['leaves'].append(math.nan)
    while len(otherDict['enters']) < len(otherDict['arrives']):
        otherDict['enters'].append(math.nan)
        otherDict['waitingTime'].append(math.nan)

    otherDict['Timelist'] = timeInterval()
    print(otherDict)
    df = pd.DataFrame(otherDict)
    print(df)
    df.plot(y= 'waitingTime', x='Timelist',  ax=plt.gca(), label='NumberMachines= {}'.format(argumentHash['NUM_MACHINES']+a), c=colors[a], drawstyle="steps" )
    if a == 0:
        plt.title("Time To Wait over Time")
        plt.show()
        df.plot(y= 'waitingTime', x='Timelist',  ax=plt.gca(), label='NumberMachines= {}'.format(argumentHash['NUM_MACHINES']+a), c=colors[a], drawstyle="steps")
plt.title("Time To Wait over Time")
plt.show()
if pos:
    data = poisson(7)
    i = 0
    for a in range(5):
        colors = ['b', 'c', 'm', 'r', 'y']
        otherDict = {'cars':[], 'arrives':[], 'enters':[], 'leaves':[], 'waitingTime': [] }
        env = simpy.Environment()
        array = []
        for num in range(0,2):
            array.append(data.rvs(num))
        env.process(setup(env, argumentHash['NUM_MACHINES'], argumentHash['WASHTIME'], array[1][0]))
        # Execute!
        env.run(until=int(argumentHash['SIM_TIME']))

        for keys in trackingDict:
            otherDict['cars'].append(keys)

            if len(trackingDict[keys]) >= 1:
                otherDict['arrives'].append(trackingDict[keys][0])
            if len(trackingDict[keys]) >= 2:
                otherDict['enters'].append(trackingDict[keys][1])
                otherDict['waitingTime'].append(float(trackingDict[keys][1])-float(trackingDict[keys][0]))
            if len(trackingDict[keys]) >= 3:
                otherDict['leaves'].append(trackingDict[keys][2])
            else:
                otherDict['leaves'].append(math.nan)
        while len(otherDict['enters']) < len(otherDict['arrives']):
            otherDict['enters'].append(math.nan)
            otherDict['waitingTime'].append(math.nan)

        otherDict['Timelist'] = timeInterval()

        df = pd.DataFrame(otherDict)
        print(df)

        df.plot(y= 'waitingTime', x='Timelist', ax=plt.gca(), label='Car Time Interval= {}'.format(array[1][0]), drawstyle='steps-post')
    #print single plot
    plt.title('Time to Wait Over Time Cars Enter')
    plt.show()