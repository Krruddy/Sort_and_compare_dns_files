class Comment:

    def __init__(self, comment: str, record = None):
        self.comment = comment
        self._record = record

    def show(self):
        print(self.comment)
        print("\n")

    def get(self):
        return self.comment

    def set(self, comment: str):
        self.comment = comment

    @property
    def record(self):
        return self._record

    @record.setter
    def record(self, record):
        if isinstance(record, Record):
            self._record = record
        if record == None:
            self._record = None
        else:
            raise TypeError("The record must be an instance of the class Record.")
