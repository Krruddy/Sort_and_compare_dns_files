import logging
from project.logger.LoggerMeta import LoggerMeta
from project.logger.CustomFormatter import CustomFormatter


class Logger(metaclass=LoggerMeta):
    def __init__(self):
        # Create a logger
        self.logger = logging.getLogger("my_logger")

        # Create a StreamHandler and set the custom formatter
        handler = logging.StreamHandler()
        handler.setFormatter(CustomFormatter())

        # Add the handler to the logger
        self.logger.addHandler(handler)

        # Set the logging level
        self.logger.setLevel(logging.INFO)

    def info(self, string: str):
        self.logger.info(string)

    def error(self, string: str):
        self.logger.error(string)

    def warning(self, string: str):
        self.logger.warning(string)