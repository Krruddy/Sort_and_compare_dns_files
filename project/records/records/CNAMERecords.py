from project.records.RecordType import RecordType
from project.records.records.AbstractRecords import AbstractRecords


class CNAMERecords(AbstractRecords):

    def __init__(self):
        super().__init__(RecordType.CNAME)

    def beautify(self):

        if len(self.records) != 0:
            longest_element = max([len(record.alias) for record in self.records])
            for record in self.records:
                added_spaces = longest_element - len(record.alias)+1
                record.alias += " " * added_spaces
                record.class_ += " " * 6
                record.type_ += " " * 7

    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.alias in seen or seen.add(x.alias))]

    def sort(self):
        self.records.sort(key=lambda x: x.alias)

    def output_lines(self):
        lines = []
        for record in self.records:
            if record.comment != None:
                lines += [record.alias + record.class_ + record.type_ + record.target + " ; " + record.comment.get() + "\n"]
            else:
                lines += [record.alias + record.class_ + record.type_ + record.target + "\n"]
        return lines
