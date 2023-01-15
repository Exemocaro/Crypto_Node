
import time
import threading

from utility.logplus import LogPlus

class TimeTracker:
    """ This class makes it easy to track the time it takes to execute a function.
    It can track multiple functions at the same time and works accross without initializing it."""

    # the time it takes to execute a function
    times = {}

    @staticmethod
    def start(name):
        """ Starts the timer for the given function name"""
        try:
            if name in TimeTracker.times:
                TimeTracker.times[name]["start"] = time.time() * 1000
                TimeTracker.times[name]["last checkpoint"] = time.time() * 1000
            else:
                TimeTracker.times[name] = {"start": time.time() * 1000,
                                            "last checkpoint": time.time() * 1000,
                                            "checkpoints": {},
                                            "ends": []}
        except Exception as e:
            LogPlus.error(f"| TimeTracker | Couldn't start {name} | {e}")   

    @staticmethod
    def checkpoint(name, checkpoint, time_from_start=False, print_directly=False):
        """ Prints the time it took to execute the function up to the given checkpoint"""
        try:
            if name in TimeTracker.times:
                current_time = time.time() * 1000
                begin_time = TimeTracker.times[name]["start"] if time_from_start else TimeTracker.times[name]["last checkpoint"]
                execution_time = round(current_time - begin_time, 2)
                TimeTracker.times[name]["last checkpoint"] = current_time
                if print_directly:
                    LogPlus.timer(f"| TimeTracker | {name} took {execution_time} ms for {checkpoint}")
                # add it to recorded checkpoints
                if checkpoint in TimeTracker.times[name]["checkpoints"]:
                    TimeTracker.times[name]["checkpoints"][checkpoint].append(execution_time)
                else:
                    TimeTracker.times[name]["checkpoints"][checkpoint] = [execution_time]
            else:
                LogPlus.error(f"| TimeTracker | Couldn't print checkpoint for {name}, it wasn't started")
        except Exception as e:
            LogPlus.error(f"| TimeTracker | Couldn't print checkpoint for {name} | {e}")

    @staticmethod
    def end(name, print_directly=False):
        """ Prints the total time it took to execute the function"""
        try:
            if name in TimeTracker.times:
                current_time = time.time() * 1000
                execution_time = round(current_time - TimeTracker.times[name]["start"], 2)
                TimeTracker.times[name]["ends"].append(execution_time)
                if print_directly:
                    LogPlus.timer(f"| TimeTracker | {name} took {execution_time} ms in total")
            else:
                LogPlus.error(f"| TimeTracker | Couldn't print total time for {name}, it wasn't started")
        except Exception as e:
            LogPlus.error(f"| TimeTracker | Couldn't print total time for {name} | {e}")

    @staticmethod
    def print_stats(name):
        """ Prints the average time it took to execute the function for each checkpoint"""
        try:
            if name in TimeTracker.times:
                LogPlus.timer(f"| TimeTracker | {name} stats:")
                for checkpoint in TimeTracker.times[name]["checkpoints"]:
                    if len(TimeTracker.times[name]["checkpoints"][checkpoint]) > 0:
                        exec_time = round(sum(TimeTracker.times[name]["checkpoints"][checkpoint]) / len(TimeTracker.times[name]["checkpoints"][checkpoint]), 2)
                    else:
                        exec_time = -1 # means it was going to be divided by 0
                    LogPlus.timer(f"| TimeTracker | {checkpoint}: {exec_time} ms")
                exec_time = round(sum(TimeTracker.times[name]["ends"]) / len(TimeTracker.times[name]["ends"]), 2)
                LogPlus.timer(f"| TimeTracker | Total: {exec_time} ms")
            else:
                LogPlus.error(f"| TimeTracker | Couldn't print stats for {name}, it wasn't started")
        except Exception as e:
            LogPlus.error(f"| TimeTracker | Couldn't print stats for {name} | {e}")

    @staticmethod
    def print_all_stats():
        """ Prints the average time it took to execute the function for each checkpoint"""
        try:
            LogPlus.timer("| TimeTracker | All stats:")
            for name in TimeTracker.times:
                TimeTracker.print_stats(name)
        except Exception as e:
            LogPlus.error(f"| TimeTracker | Couldn't print all stats | {e}")

    @staticmethod
    def regularly_print_stats():
        """ Works multithreaded, prints the stats every 5 seconds"""
        def print_stats():
            TimeTracker.print_all_stats()
            threading.Timer(5, print_stats).start()
        print_stats()