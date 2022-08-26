
import statistics
from time import time
from uuid import uuid4


class OperationTimer:
    def __init__(self, name):
        self.name = name
        self.startedTimers = {}
        self.measuredTimes = []
        self.totalTime = 0

    def start_timer(self, verbose=False):
        id = uuid4()
        self.startedTimers[id] = time()

        if verbose:
            print("started", self.name, id, self.startedTimers[id])

        return id

    def end_timer(self, id, verbose=False):
        end = time()
        start = self.startedTimers[id]
        del self.startedTimers[id]

        elapsedTime = end - start
        self.measuredTimes.append(elapsedTime)
        self.totalTime += elapsedTime

        if verbose:
            print("ending", self.name, id, elapsedTime)

        return elapsedTime

    def stats(self):
        st = {
            "total": self.totalTime,
            "count": len(self.measuredTimes),
            "mean": statistics.mean(self.measuredTimes)
        }

        if len(self.measuredTimes) > 1:
            st["variance"] = statistics.variance(self.measuredTimes)
        else:
            st["variance"] = 0

        return st

class Timer:
    def __init__(self):
        self.timers = {}

    def start_operation(self, name):
        if self.timers.get(name) == None:
            self.timers[name] = OperationTimer(name)

        id = self.timers[name].start_timer()

        return id

    def end_operation(self, name, id, verbose=False):
        self.timers[name].end_timer(id, verbose)

    def stats(self):
        allStats = []
        for key in self.timers:
            print(key)
            allStats.append({"name": key, "stats": self.timers[key].stats()})

        return allStats

sharedTimer = Timer()


        