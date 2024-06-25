from project.records.RecordType import RecordType
from project.records.records.ARecords import ARecords
from project.records.records.CNAMERecords import CNAMERecords
from project.records.records.NSRecords import NSRecords
from project.records.records.PTRRecords import PTRRecords
from project.records.records.SOARecords import SOARecords


class DNSRecords:

    def __init__(self, forward: bool = True):
        self.is_forward = forward
        self.A_records = ARecords()
        self.CNAME_records = CNAMERecords()
        self.NS_records = NSRecords()
        self.PTR_records = PTRRecords()
        self.SOA_records = SOARecords()
        self.all_records = {
            RecordType.A: self.A_records,
            RecordType.CNAME: self.CNAME_records,
            RecordType.PTR: self.PTR_records
        }


    def show_records(self):
        for record_type in self.all_records:
            record_type.show_records()

    def show_number_of_records(self):
        for record_type in self.all_records:
            record_type.show_number_of_records()

    def beautify(self):
        for record_type in self.all_records:
            record_type.beautify()

    def remove_duplicates(self):
        for record_type in self.all_records:
            record_type.remove_duplicates()

    def sort(self):
        for record_type in self.all_records:
            record_type.sort()

    def trim(self):
        for record_type in self.all_records:
            record_type.trim()

    def output_lines(self):
        lines = []

        for record_type in self.all_records:
            lines.extend(record_type.output_lines())

        return lines
