import heapq
import itertools

# Customer Typ 1       interStation    Schlange zu lang    wie viel kaufen
# Baecker               10s             10                   10
# Wurst                 30s             10                   5
# Kaese                 45s             5                    3
# Kasse                 60s             20                   30

# Customer Typ 2
# Wurst                 30s             5                    2
# Kasse                 30s             20                   3
# Baecker               20s             20                   3

# Baecker   per article     10s
# Wurst     per article     30s
# Kaese     per article     60s
# Kasse     per article     5s

# Tuple for EventQueue
#       time, priority, number, function, opt(args)

eventNumber = itertools.count()
shoppingTime = []
globalCustomerCount = 0
globalTime = 0


class Customer:

    def __init__(self, name, customerType, startTime):

        self.name = name
        self.nextStation = []
        self.served = True
        self.startTime = startTime

        # •	Bäcker, •	Wursttheke,
        # •	Käsetheke, •	Kasse
        self.upcomingStations = []
        self.visit = []

        if customerType == 1:
            self.upcomingStations = [(10, 10, 10), (30, 10, 5), (45, 5, 3), (60, 20, 30)]
            self.visit = [0, 1, 2, 3]
        else:
            self.upcomingStations = [(20, 20, 3), (30, 5, 2), (0, 0, 0), (30, 20, 3)]
            self.visit = [1, 3, 0]

    def startShopping(self, argList):

        global globalCustomerCount
        globalCustomerCount = globalCustomerCount + 1
        print(self.name + " starts at " + str(globalTime) + "s")
        return self.goToStation([])

    def goToStation(self, argList):

        self.nextStation = self.visit.pop(0)
        # self.nextStation = self.visit.pop(1)
        return [[globalTime + self.upcomingStations[self.nextStation][0], 3, next(eventNumber),
                 self.arriveAtStation, [self.nextStation]]]

    def arriveAtStation(self, argList):
        currentStationIndex = argList[0]
        currentStation = stations[currentStationIndex]

        if len(currentStation.waitingQueue) < self.upcomingStations[currentStationIndex][1]:
            if currentStation.serves:
                print(self.name + " queues at Station " + stations[argList[0]].name + " at time " + str(
                    globalTime) + "s")
                currentStation.waitingQueue.append(self)
            else:
                return self.startStation(argList)
        else:
            self.served = False
            currentStation.customersSkipped = currentStation.customersSkipped + 1
            return self.goToStation(argList)

    def startStation(self, argList):
        print(self.name + " starts Station " + stations[argList[0]].name + " at time " + str(globalTime) + "s")

        currentStation = argList[0]
        stations[currentStation].serves = True

        perProduct = stations[currentStation].serviceTime

        return [[globalTime + (perProduct * self.upcomingStations[currentStation][2]),
                 1,
                 next(eventNumber),
                 self.finishedAtStation,
                 [currentStation]]]

    def finishedAtStation(self, argList):

        print(self.name + " finished Station " + stations[argList[0]].name + " at time " + str(globalTime) + "s")
        stations[argList[0]].serves = False

        nextCustomerInQueueEvent = []
        if len(stations[argList[0]].waitingQueue) > 0:
            currentUser = stations[argList[0]].waitingQueue.pop(0)
            tempList = currentUser.startStation([currentUser.nextStation])
            for entry in tempList:
                for x in entry:
                    nextCustomerInQueueEvent.append(x)

        if len(self.visit) == 0:

            shoppingTime.append((self.name, globalTime - self.startTime, globalTime))
            print(self.name + " finished shopping at " + str(globalTime) + "s")
            return [[-1, 10, 0, None, []]]

        retVal = self.goToStation([])
        retVal.append(nextCustomerInQueueEvent)
        return retVal


class Station:
    def __init__(self, name, serviceTime):
        self.name = name
        self.serviceTime = serviceTime
        self.waitingQueue = []
        self.serves = False
        self.customersSkipped = 0


class EventQueue:
    #       time, priority, number, function, opt(args)

    def __init__(self):
        self.queue = []
        self.time = 0
        self.eventCount = 0

    def pop(self):
        return heapq.heappop(self.queue)

    def push(self, event):
        heapq.heappush(self.queue, event)

    def run(self):
        global eventNumber
        cus1 = Customer("type1 1", 1, 0)
        self.push([0, 5, next(eventNumber), cus1.startShopping, []])

        cus2 = Customer("type2 1", 2, 1)
        self.push([1, 5, next(eventNumber), cus2.startShopping, []])

        cus3 = Customer("type2 2", 2, 61)
        self.push([61, 5, next(eventNumber), cus3.startShopping, []])

        cus4 = Customer("type2 3", 2, 121)
        self.push([121, 5, next(eventNumber), cus4.startShopping, []])

        cus5 = Customer("type2 4", 2, 181)
        self.push([181, 5, next(eventNumber), cus5.startShopping, []])

        """cus4 = Customer("type1 3", 2, 121)
        self.push([1221, 2, next(eventNumber), cus4.startShopping, []])

        cus5 = Customer("type1 4", 2, 181)
        self.push([10, 2, next(eventNumber), cus5.startShopping, []])
        """
        cus6 = Customer("type1 3", 1, 200)
        self.push([200, 5, next(eventNumber), cus6.startShopping, []])

        cus7 = Customer("type2 5", 2, 241)
        self.push([241, 5, next(eventNumber), cus7.startShopping, []])

        while len(self.queue) > 0:

            global globalTime
            time, priority, eventNumber2, function, args = self.pop()

            if time == -1 and len(self.queue) == 0:
                print("\n\n--end--")
                return

            elif time == -1:
                continue

            elif globalTime < time:
                globalTime = globalTime + 1
                self.push([time, priority, eventNumber2, function, args])
                continue

            else:
                tmp = function(args)
                if tmp is not None:
                    for lst in tmp:
                        if len(lst) != 0:
                            self.push([lst[0], lst[1], lst[2], lst[3], lst[4]])

                globalTime = globalTime + 1


eventQueue = EventQueue()
stations = [Station("Baker", 10), Station("Butcher", 30), Station("Cheese counter", 60), Station("Checkout", 5)]
eventQueue.run()
(customerName, timeTaken, endTime) = shoppingTime.pop()
shoppingTime.append((customerName, timeTaken, endTime))

print("Simulationsende: " + str(endTime) + "s")
print("Anzahl Kunden: 7")
print("Anzahl vollständige Einkäufe: " + str(len(shoppingTime)))
customerFullyServedCount = len(shoppingTime)
customerShoppingTimeSum = 0

for i in range(len(shoppingTime)):
    (customerName, timeTaken, endTime) = shoppingTime.pop(0)
    shoppingTime.append((customerName, timeTaken, endTime))
    customerShoppingTimeSum = customerShoppingTimeSum + timeTaken

print("Mittlere Einkaufsdauer: " + str(customerShoppingTimeSum / customerFullyServedCount))

# percentage that skipped

for station in stations:
    print(
        "Drop Percentage at " + station.name + ": " + str((station.customersSkipped / globalCustomerCount) * 10) +
        "%")
