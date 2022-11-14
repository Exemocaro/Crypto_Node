import logging
from colorama import Fore, Back, Style

from config import *

# LogPlus is like logging, but it also prints the message


class LogPlus:

    @staticmethod
    def debug(message):
        """ if len(message) > LOG_LIMIT:
            message = message[0:LOG_LIMIT]
        logging.debug(message)
        print(message) """
        pass

    @staticmethod
    def info(message):
        """ if len(message) > LOG_LIMIT:
            message = message[0:LOG_LIMIT]
        logging.info(message)
        print(message) """
        pass

    @staticmethod
    def warning(message):
        if len(message) > LOG_LIMIT:
            message = message[0:LOG_LIMIT]
        logging.warning(message)
        print(Fore.YELLOW + message + Style.RESET_ALL)

    @staticmethod
    def error(message):
        if len(message) > LOG_LIMIT:
            message = message[0:LOG_LIMIT]
        logging.error(message)
        print(Fore.RED + message + Style.RESET_ALL)

    @staticmethod
    def critical(message):
        if len(message) > LOG_LIMIT:
            message = message[0:LOG_LIMIT]
        logging.critical(message)
        print(message)
