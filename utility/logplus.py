import logging

# LogPlus is like logging, but it also prints the message


class LogPlus:

    @staticmethod
    def debug(message):
        logging.debug(message)
        print(message)

    @staticmethod
    def info(message):
        logging.info(message)
        print(message)

    @staticmethod
    def warning(message):
        logging.warning(message)
        print(message)

    @staticmethod
    def error(message):
        logging.error(message)
        print(message)

    @staticmethod
    def critical(message):
        logging.critical(message)
        print(message)
