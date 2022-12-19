import logging
from colorama import Fore, Back, Style

from config import *

# LogPlus is like logging, but it also prints the message


class LogPlus:

    @staticmethod
    def debug(message):
        if len(message) > LOG_LIMIT:
            message = message[0:LOG_LIMIT]
        #logging.debug(message)
        #print(Fore.GREEN + message + Style.RESET_ALL)
        pass

    @staticmethod
    def info(message):
        if len(message) > LOG_LIMIT:
            message = message[0:LOG_LIMIT]
        #logging.info(message)
        #print(message)
        pass

    @staticmethod
    def warning(message):
        if len(message) > LOG_LIMIT:
            logging.warning(message[0:LOG_LIMIT])
            print(Fore.YELLOW + message[0:LOG_LIMIT] + Style.RESET_ALL)
        else:
            logging.warning(message)
            print(Fore.YELLOW + message + Style.RESET_ALL)

    @staticmethod
    def error(message):
        if len(message) > LOG_LIMIT:
            logging.error(message[0:LOG_LIMIT])
            print(Fore.RED + message[0:LOG_LIMIT] + Style.RESET_ALL)
        else:
            logging.warning(message)
            print(Fore.RED + message + Style.RESET_ALL)

    @staticmethod
    def critical(message):
        if len(message) > LOG_LIMIT:
            logging.critical(message[0:LOG_LIMIT])
            print(message[0:LOG_LIMIT])
        else:
            logging.warning(message)
            print(Fore.RED + message + Style.RESET_ALL)
