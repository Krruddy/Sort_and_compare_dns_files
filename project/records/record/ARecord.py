from project.records.record.AbstractRecord import AbstractRecord


class ARecord(AbstractRecord):

    def __init__ (self, server_name: str, TTL: int = None, class_: str = "IN", type_: str = "A", target: str = None, comment = None):
        super().__init__(TTL, class_, type_, comment)
        self.server_name = server_name
        self.target = target

    def __eq__(self, other):
        if isinstance(other, ARecord):
            return (
                    self.server_name == other.server_name and
                    self.class_ == other.class_ and
                    self.type_ == other.type_ and
                    self.target == other.target
            )

    # Trim every attribute of the class
    def trim(self):
        super().trim()
        self.server_name = self.server_name.strip()
        self.target = self.target.strip()

    def show(self):
        super().show()
        print(f"server name : {self.server_name}")
        print(f"target : {self.target}\n")
