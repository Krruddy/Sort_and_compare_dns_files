from typing import List
from pathlib import Path

from project.files.DNSFile import DNSFile
from project.logger.Logger import Logger


class Sorter:
    def __init__(self, files: List[Path]):
        self.logger = Logger()
        self.files = files
        self.__set_DNS_files()

    # TODO Create the DNSFiles outside of the sorter and the comparator
    def __set_DNS_files(self):
        self.dns_files = {}
        for file in self.files:
            if file.is_file():
                self.dns_files[file.name] = DNSFile(file)

    def sort(self):
        for dns_file in self.dns_files.values():
            dns_file.sort()
