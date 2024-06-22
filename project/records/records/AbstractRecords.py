from project.records.record.AbstractRecord import AbstractRecord

class AbstractRecords:

    def __init__(self):
        self.records = []

    def add_record(self, record: AbstractRecord):
        self.records += [record]

    def remove_record(self, record: AbstractRecord):
        self.records.remove(record)

    def simple_compare(self, left, right):
        if isinstance(left, AbstractRecords) and isinstance(right, AbstractRecords):
            left.simple_compare(right)
        else:
            raise TypeError("The objects must be instances of the class Record.")

    def show_records(self):
        for record in self.records:
            record.show()
            print("\n")

    def show_number_of_records(self):
        print(f"Number of records : {len(self.records)}")

    def trim(self):
        for record in self.records:
            record.trim()

    def number_of_records(self):
        return len(self.records)
