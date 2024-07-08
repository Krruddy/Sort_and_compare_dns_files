from project.records.RecordType import RecordType
from project.records.records.AbstractRecords import AbstractRecords


class NSRecords(AbstractRecords):

    def __init__(self):
        super().__init__(RecordType.NS)

    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.target in seen or seen.add(x.target))]

    def sort(self):
        if len(self.records) >= 4:
            primary_and_secondary_ns = self.records[:2]
            rest = self.records[2:]
            rest.sort(key=lambda x: getattr(x, "zone"))
            self.records = primary_and_secondary_ns + rest
        else:
            pass

    def generate_output(self):
        output = ""
        for i, record in enumerate(self.records):
            if i == 2:
                output += "\n"
            output += record.generate_output() + "\n"
        output += "\n"
        return output
