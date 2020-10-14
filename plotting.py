import subprocess
import re
import pandas as pd
import matplotlib.pyplot  as plt
import sys as sys
from scipy.stats import poisson


data = poisson(7)
process1 = subprocess.Popen(['python', 'carwash.py', '-r', '42', '-m', '2' ,'-w', '5', '-t', '4' ,'-s', '500'], stdout=subprocess.PIPE)
process2 = subprocess.Popen(['python', 'carwash.py', '-r', '42', '-m', '1' ,'-w', '5', '-t', '4' ,'-s', '500'], stdout=subprocess.PIPE)
process3 = subprocess.Popen(['python', 'carwash.py', '-r', '42', '-m', '3' ,'-w', '5', '-t', '4' ,'-s', '500'], stdout=subprocess.PIPE)
allProcess = []
print(len(sys.argv))
if len(sys.argv) >1 :
    allProcess = [process1, process2, process3]
else:
    allProcess = range(0,10)
i = 0
for processes in allProcess:#range(0,10):

    numberOfMachines = [2,3,4]
    array = []
    process = None
    for num in range(0,2):
        array.append(data.rvs(num))
    if  len(sys.argv) > 1:
        process = processes
    else:
        process = subprocess.Popen(['python', 'carwash.py', '-r', '42', '-m', '2' ,'-w', '5', '-t', '{}'.format(array[1][0]) ,'-s', '60'], stdout=subprocess.PIPE)

    out, err = process.communicate()
    outCensor = "\n".join(str(out).splitlines())
    outCensorArray = outCensor.split("\\n")



    trackingDict = {}
    outCensorArray[0] = outCensorArray[0].replace("b\"", "")

    for a in outCensorArray:
        #print(a)
        enters = re.match("Car (\d+\d{0,1}) *enters.* at (\d\d{0,1}\.\d\d)",a)
        arrives = re.match("Car (\d+\d{0,1}) *arrives.* at (\d\d{0,1}\.\d\d)",a)
        leaves = re.match("Car (\d+\d{0,1}) *leaves.* at (\d\d{0,1}\.\d\d)",a)
        percentCleaned = re.match("Carwash removed (\d\d{0,1}).* Car (\d\d{0,1})\'s", a)
        if arrives:
            #print (arrives.group(1) + " " + arrives.group(2))
            trackingDict[arrives.group(1)] = [arrives.group(2)]
        if enters:
            #print (enters.group(1) + " " + enters.group(2))
            trackingDict[enters.group(1)].append(enters.group(2))
        if leaves:
            trackingDict[leaves.group(1)].append(leaves.group(2))
        if percentCleaned:
            trackingDict[percentCleaned.group(2)].append(percentCleaned.group(1))

    otherDict = {'cars':[], 'arrives':[], 'enters':[], 'percentCleaned':[],'leaves':[], 'waitingTime': [] }
    for keys in trackingDict:
        otherDict['cars'].append(keys)
        if len(trackingDict[keys]) >= 1:
            otherDict['arrives'].append(trackingDict[keys][0])
        if len(trackingDict[keys]) >= 2:
            otherDict['enters'].append(trackingDict[keys][1])
            otherDict['waitingTime'].append(float(trackingDict[keys][1])-float(trackingDict[keys][0]))

        if len(trackingDict[keys]) >= 3:
            otherDict['percentCleaned'].append(trackingDict[keys][2])
        else:
            otherDict['percentCleaned'].append("NaN")
        if len(trackingDict[keys]) >= 4:
            otherDict['leaves'].append(trackingDict[keys][3])
        else:
            otherDict['leaves'].append("NaN")

    print(otherDict['waitingTime'])
    if len(sys.argv) >1 :
        df = pd.DataFrame(otherDict)
        df.plot(y= 'waitingTime', x='enters', ax=plt.gca(), label='NumberMachines= {}'.format(numberOfMachines[i]))
    else:
        df = pd.DataFrame(otherDict)
        df.plot(y= 'waitingTime', x='enters', ax=plt.gca(), label='Car Time Interval= {}'.format(array[1][0]))
    i += 1
plt.title("Time To Wait over Time cars enter")
plt.show()

