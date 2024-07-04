from pathlib import Path
from typing import List
import os

from project.files.DNSFile import DNSFile
from project.logger.Logger import Logger
from project.records.RecordType import RecordType


class Comparator:
    def __init__(self, files: List[Path], loom: Path):
        self.logger = Logger()
        self.files = files
        self.__set_DNS_files()
        self.__set_LOOM_files(loom)

    def __set_LOOM_files(self, loom: Path):
        self.loom_files = {}
        if loom.is_dir():
            for file in self.files:
                if file.is_file():
                    if (loom_file := self.find_file(loom, file.name)) is not None:
                        self.loom_files[file.name] = DNSFile(loom_file)
        # TODO else: raise error

    def find_file(self, directory: Path, filename) -> Path | None:
        for root, dirs, files in os.walk(directory):
            if filename in files:
                return Path(os.path.join(root, filename))
        return None

    def __set_DNS_files(self):
        self.dns_files = {}
        for file in self.files:
            if file.is_file():
                self.dns_files[file.name] = DNSFile(file)

    def compare(self):
        for file in self.files:
            if file.name in self.dns_files and file.name in self.loom_files:
                for record_type in self.dns_files[file.name].records:
                        loom_file = self.loom_files[file.name]
                        first_attribute = {
                            RecordType.A: "server_name",
                            #RecordType.NS: "TTL",
                            RecordType.CNAME: "alias",
                            #RecordType.SOA: "mname",
                            RecordType.PTR: "ip"
                        }
                        fourth_attribute = {
                            RecordType.A: "target",
                            #RecordType.NS: "name_server",
                            RecordType.CNAME: "target",
                            #RecordType.SOA: "rname",
                            RecordType.PTR: "domain_name"
                        }


                        # TODO: Use sub-methods to make it more readable

                        # New algorithm
                        # record is in dns but not in loom
                        #       if same first attribute => append records_same_first_attribute
                        #       if same fourth attribute => append to records_same_fourth_attribute
                        #       else  => append to records_not_in_DNS


                        records_not_in_DNS = []

                        for loom_record in loom_file.records[record_type].records:
                            if loom_record not in self.dns_files[file.name].records[record_type].records:
                                records_not_in_DNS.append(loom_record)

                        records_same_first_attribute = []
                        records_same_fourth_attribute = []

                        for loom_record in loom_file.records[record_type].records:
                            if loom_record in self.dns_files[file.name].records[record_type].records:
                                pass
                            else:
                                for dns_record in self.dns_files[file.name].records[record_type].records:
                                    if loom_record.__dict__[first_attribute[record_type]] == dns_record.__dict__[first_attribute[record_type]]:
                                        records_same_first_attribute.append(loom_record)
                                    elif loom_record.__dict__[fourth_attribute[record_type]] == dns_record.__dict__[fourth_attribute[record_type]]:
                                        records_same_fourth_attribute.append(loom_record)

                        # Ask the user if the DNS records should be updated to match the LOOM entries.

                        for record in records_not_in_DNS:
                            print("\n", "-" * 80, "\n")










