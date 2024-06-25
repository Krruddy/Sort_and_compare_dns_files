import re
import os
from pathlib import Path

import dns

from project.logger.Logger import Logger
from project.records.DNSRecords import DNSRecords
from project.records.record.ARecord import ARecord
from project.records.record.CNAMERecord import CNAMERecord
from project.records.record.NSRecord import NSRecord
from project.records.record.PTRRecord import PTRRecord
from project.records.record.SOARecord import SOARecord


class LOOMFile:
    def __init__(self, loom_path: Path, is_forward: bool):
        self.logger = Logger()
        self.path = loom_path
        self.is_forward = is_forward
        self.__set_TTL()
        self.__set_DNS_records()

    def __set_TTL(self):
        with open(self.path, "r") as file:
            for line in file:
                if "$TTL" in line:
                    self.TTL = int(line.split()[1])
                    break
        # TODO : handle the case where a TTL is not found

    def __set_DNS_records(self):
        self.records = DNSRecords(self.is_forward)
        # TODO : removing "manually" the lines that contain "$TTL" is more robust
        file_content = '\n'.join(open(self.path, "r").read().split('\n')[1:])
        zone = dns.zone.from_text(file_content, origin="", relativize=False, check_origin=False)

        for name, node in zone.nodes.items():
            for rdataset in node.rdatasets:
                for rdata in rdataset:
                    if rdataset.rdtype == 1:  # A
                        current_record = ARecord(server_name=name.to_text(),
                                                 class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                 type_=dns.rdatatype.to_text(rdataset.rdtype), target=rdata.to_text())
                        current_record.show()
                        self.records.A_records.add_record(current_record)
                    elif rdataset.rdtype == 2:  # NS
                        current_record = NSRecord(server_name=name.to_text(),
                                                  class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                  type_=dns.rdatatype.to_text(rdataset.rdtype), target=rdata.to_text())
                        current_record.show()
                        self.records.NS_records.add_record(current_record)
                    elif rdataset.rdtype == 5:  # CNAME
                        current_record = CNAMERecord(alias=name.to_text(),
                                                     class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                     type_=dns.rdatatype.to_text(rdataset.rdtype),
                                                     target=rdata.to_text())
                        current_record.show()
                        self.records.CNAME_records.add_record(current_record)
                    elif rdataset.rdtype == 6:  # SOA
                        current_record = SOARecord(primary_name_server=rdata.mname.to_text(),
                                                   hostmaster=rdata.rname.to_text(),
                                                   serial=rdata.serial,
                                                   refresh=rdata.refresh,
                                                   retry=rdata.retry,
                                                   expire=rdata.expire,
                                                   minimum_ttl=rdata.minimum)
                        current_record.show()
                        self.records.SOA_records.add_record(current_record)
                    elif rdataset.rdtype == 12:  # PTR
                        current_record = PTRRecord(ip=name.to_text(), class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                   type_=dns.rdatatype.to_text(rdataset.rdtype),
                                                   domain_name=rdata.to_text())
                        current_record.show()
                        self.records.PTR_records.add_record(current_record)

    def show_records(self):
        self.records.show_records()
