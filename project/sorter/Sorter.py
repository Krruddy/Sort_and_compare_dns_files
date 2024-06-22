from typing import List
from pathlib import Path

from project.logger.Logger import Logger


class Sorter:
    def __init__(self, files: List[Path]):
        self.logger = Logger()
        self.files = files
    def sort(self):
        for file in self.files:
            if file.is_file():


