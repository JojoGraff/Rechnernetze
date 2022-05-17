from threading import Thread, Event, Lock
from time import sleep
from operator import itemgetter

newTyp1 = 1
newTyp2 = 1
transactionList = []
fullyServedCustomers = 0
customerCount = 0

SLEEP_INTERVAL = 0.002
GEN_TIME = 1800
SIMULATION_LENGTH = 3100
globalTime = 0


class Customer(Thread):

    def __init__(self, name, customerType):
        Thread.__init__(self)
        self.name = name
        self.waitToBeServedEv = Event()
        self.served = True
        if customerType == 1:

            self.upcomingStations = [(10, 10, 10), (30, 10, 5), (45, 5, 3), (60, 20, 30)]
            self.visit = [0, 1, 2, 3]
        else:
            self.upcomingStations = [(20, 20, 3), (30, 5, 2), (0, 0, 0), (30, 20, 3)]
            self.visit = [1, 3, 0]

        self.nextStation = 0

    def startStation(self):

        currentStation = stations[self.nextStation]
        print("\ncustomer: " + self.name + " started at station " + currentStation.name)

        currentStation.serveTimeForNextCustomer = currentStation.timePerProduct * \
                                                  self.upcomingStations[self.nextStation][2]

        currentStation.ownArrEv.set()
        print("customer: " + self.name + " is being served " + currentStation.name)
        currentStation.ownServEv.wait()

        print("customer: " + self.name + " finished at station " + currentStation.name)

    def arriveAtStation(self):
        currentStation = stations[self.nextStation]

        currentStation.waitQueueLock.acquire()
        if currentStation.ownArrEv.is_set():

            if len(currentStation.waitingQueue) < self.upcomingStations[self.nextStation][1]:
                print("customer: " + self.name + " queues at station " + stations[self.nextStation].name)
                currentStation.waitingQueue.append(self)
                currentStation.waitQueueLock.release()
                self.waitToBeServedEv.wait()

            else:
                currentStation.waitQueueLock.release()
                print("customer: " + self.name + " skips station " + stations[self.nextStation].name)
                currentStation.customersSkipped = currentStation.customersSkipped + 1
                self.served = False

                return

        else:
            currentStation.waitQueueLock.release()
        self.startStation()

    def goToStation(self):
        self.nextStation = self.visit.pop(0)
        print("customer: " + self.name +
              " goes to station " + stations[self.nextStation].name)

        serveSleep(self.upcomingStations[self.nextStation][0])

    def run(self):
        print("customer: " + self.name + " arrived at the shop")
        global customerCount
        customerCount = customerCount + 1

        startTime = globalTime
        while len(self.visit) > 0:
            self.goToStation()
            self.arriveAtStation()

        """while len(self.visit) < 0:
            self.goToStation()
            self.arriveAtStation()"""

        if self.served:
            global fullyServedCustomers
            fullyServedCustomers = fullyServedCustomers + 1

        endTimeTmp = globalTime
        timeNeeded = endTimeTmp - startTime
        if self.served:
            transactionList.append((self.name, timeNeeded, endTimeTmp))
        print("customer: " + self.name + " finished shopping")


class Station(Thread):

    def __init__(self, name, timePerProduct):
        print(name + " started to init")
        Thread.__init__(self)
        self.name = name
        self.timePerProduct = timePerProduct
        self.serveTimeForNextCustomer = 0
        self.customersSkipped = 0

        self.waitingQueue = []
        self.serves = False
        self.ownArrEv = Event()
        self.ownServEv = Event()
        self.nextInQueue = Event()
        self.waitQueueLock = Lock()

    def waitForCustomer(self):
        while not globalStationStopEvent.is_set():
            self.ownArrEv.wait(timeout=SLEEP_INTERVAL)
            if self.ownArrEv.is_set():
                return

        print(self.name + " exited by Event")
        exit(11)

    def serve(self):
        print("station: " + self.name + " started to serve")
        serveSleep(self.serveTimeForNextCustomer)
        print("station: " + self.name + " finished to serve")
        self.ownServEv.set()

        self.ownServEv.clear()

    def run(self):
        print(self.name + " started")

        while True:
            self.waitForCustomer()
            self.serve()

            self.waitQueueLock.acquire()
            while len(self.waitingQueue) > 0:
                nextCustomer = self.waitingQueue.pop(0)
                self.waitQueueLock.release()
                nextCustomer.waitToBeServedEv.set()
                nextCustomer.waitToBeServedEv.clear()

                self.serve()
                self.waitQueueLock.acquire()

            self.ownArrEv.clear()
            self.waitQueueLock.release()


def serveSleep(time):
    until = globalTime + time
    while until > globalTime:
        sleep(SLEEP_INTERVAL / 3)
    return


def startCustomer(name, typ):
    customer1 = Customer(name, typ)
    customer1.start()


globalStationStopEvent = Event()

stations = [Station("Baker", 10), Station("Butcher", 30), Station("Cheese counter", 60), Station("Checkout", 5)]

for stat in stations:
    stat.start()

for i in range(0, SIMULATION_LENGTH):
    print("CurrentTime: " + str(globalTime) + "s")
    if (globalTime % 200) == 0 and globalTime < GEN_TIME:
        startCustomer(str(newTyp1) + "-Typ1", 1)
        newTyp1 = newTyp1 + 1
    if (globalTime % 60) == 1 and globalTime < GEN_TIME:
        startCustomer(str(newTyp2) + "-Typ2", 2)
        newTyp2 = newTyp2 + 1

    sleep(SLEEP_INTERVAL)
    globalTime = globalTime + 1

print("\n\n--end--")
globalStationStopEvent.set()

(customer, timeNeeded, endTime) = transactionList.pop()
transactionList.append((customer, timeNeeded, endTime))

lastShopper = max(transactionList, key=itemgetter(2))
customerFullyServedCount = len(transactionList)
customerShoppingTimeSum = 0
for i in range(len(transactionList)):
    (customerName, timeTaken, endTime) = transactionList.pop(0)
    transactionList.append((customerName, timeTaken, endTime))
    customerShoppingTimeSum = customerShoppingTimeSum + timeTaken

print("Simulationsende: " + str(endTime) + "s")
print("Anzahl Kunden: " + str(customerCount))
print("Anzahl vollständige Einkäufe: " + str(len(transactionList)))
print("Mittlere Einkaufsdauer: " + str(round((customerShoppingTimeSum / customerFullyServedCount), 2)) + "s")
for station in stations:
    print(
        "Drop percentage at " + station.name + ": " + str((station.customersSkipped / customerCount) * 100)[0:4] + "%")
sleep(3)
exit(0)
