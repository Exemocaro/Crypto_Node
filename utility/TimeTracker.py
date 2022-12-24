
import time

from utility.logplus import LogPlus

class TimeTracker:
    """ This class makes it easy to track the time it takes to execute a function.
    It can track multiple functions at the same time and works accross without initializing it."""

    # the time it takes to execute a function
    times = {}

    @staticmethod
    def start(name):
        """ Starts the timer for the given function name"""
        TimeTracker.times[name] = time.time() / 1000

    @staticmethod
    def checkpoint(name, checkpoint):
        """ Prints the time it took to execute the function up to the given checkpoint"""
        if name in TimeTracker.times:
            current_time = time.time() / 1000
            execution_time = current_time - TimeTracker.times[name]
            LogPlus.info(f"| TimeTracker | {name} took {execution_time} seconds to execute up to {checkpoint}")
        else:
            LogPlus.error(f"| TimeTracker | Couldn't print checkpoint for {name}, it wasn't started")
