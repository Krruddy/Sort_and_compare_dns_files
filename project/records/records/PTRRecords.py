from project.records.RecordType import RecordType
from project.records.records.AbstractRecords import AbstractRecords

class PTRRecords(AbstractRecords):

    def __init__(self):
        super().__init__(RecordType.PTR)

    def beautify(self):
        if len(self.records) != 0:
            longest_element = max([len(record.ip) for record in self.records])
            for record in self.records:
                added_spaces = longest_element - len(record.ip)+1
                record.ip += " " * added_spaces
                record.class_ += " " * 6
                record.type_ += " " * 7

    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.ip in seen or seen.add(x.ip))]

    def sort(self):
        self.records.sort(key=lambda x: list(map(int, x.ip.split('.'))))

    def output_lines(self):
        lines = []
        for record in self.records:
            if record.comment != None:
                lines += [record.ip + record.class_ + record.type_ + record.domain_name + " ; " + record.comment.get() + "\n"]
            else:
                lines += [record.ip + record.class_ + record.type_ + record.domain_name + "\n"]
        return lines