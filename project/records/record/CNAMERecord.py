from project.records.record.AbstractRecord import AbstractRecord


class CNAMERecord(AbstractRecord):

    def __init__ (self, alias: str, TTL: int = None, class_: str = "IN", type_: str = "CNAME", target: str = None, comment = None):
        super().__init__(TTL, class_, type_, comment)
        self.alias = alias
        self.target = target

    def __eq__(self, other):
        if isinstance(other, CNAMERecord):
            return (
                    self.alias == other.alias and
                    self.class_ == other.class_ and
                    self.type_ == other.type_ and
                    self.target == other.target
            )

    # Trim every attribute of the class
    def trim(self):
        super().trim()
        self.alias = self.alias.strip()
        self.target = self.target.strip()

    def show(self):
        super().show()
        print(f"domain name : {self.alias}")
        print(f"target : {self.target}\n")
