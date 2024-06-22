from project.records.records.AbstractRecords import AbstractRecords


class SOARecords(AbstractRecords):

    def __init__(self):
        super().__init__()

        def beautify(self):
            if len(self.records) != 0:
                longest_element = max([len(record.primary_name_server) for record in self.records])
                for record in self.records:
                    added_spaces = longest_element - len(record.primary_name_server)+1
                    record.primary_name_server += " " * added_spaces
                    record.class_ += " " * 6
                    record.type_ += " " * 7

        def remove_duplicates(self):
            seen = set()
            self.records = [x for x in self.records if not (x.primary_name_server in seen or seen.add(x.primary_name_server))]

        def sort(self):
            self.records.sort(key=lambda x: x.primary_name_server)

        def output_lines(self):
            lines = []
            for record in self.records:
                lines += [record.generate_output() + "\n"]
            return lines
