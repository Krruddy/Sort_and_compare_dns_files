from project.records.records.AbstractRecords import AbstractRecords


class ARecords(AbstractRecords):

    def __init__(self):
        super().__init__()

    def beautify(self):
        if len(self.records) != 0:
            longest_element = max([len(record.server_name) for record in self.records])
            for record in self.records:
                added_spaces = longest_element - len(record.server_name)+1
                record.server_name += " " * added_spaces
                record.class_ += " " * 6
                record.type_ += " " * 7

    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.target in seen or seen.add(x.target))]

    def sort(self):
        for record in self.records:
            print(record.target)
        self.records.sort(key=lambda x: list(map(int, x.target.split('.'))))

    def output_lines(self):
        lines = []
        for record in self.records:
            if record.comment != None:
                lines += [record.server_name + record.class_ + record.type_ + record.target + " ; " + record.comment.get() + "\n"]
            else:
                lines += [record.server_name + record.class_ + record.type_ + record.target + "\n"]
        return lines

