from project.records.RecordType import RecordType
from project.records.records.AbstractRecords import AbstractRecords


class ARecords(AbstractRecords):
    def __init__(self):
        super().__init__(RecordType.A)

    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.target in seen or seen.add(x.target))]

    # Sort based on IP address
    def sort(self):
        self.records.sort(key=lambda x: tuple(int(part) for part in x.target.split('.')))

    def output_lines(self):
        lines = []
        for record in self.records:
            if record.comment != None:
                lines += [
                    record.server_name + record.class_ + record.type_ + record.target + " ; " + record.comment.get() + "\n"]
            else:
                lines += [record.server_name + record.class_ + record.type_ + record.target + "\n"]
        return lines
