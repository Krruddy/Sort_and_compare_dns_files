from project.records.record.AbstractRecord import AbstractRecord


class PTRRecord(AbstractRecord):
    def __init__ (self, ip: str, TTL: int = None, class_: str = "IN", type_: str = "PTR", domain_name: str = None, comment = None):
        super().__init__(TTL, class_, type_, comment)
        self.ip = ip if ip[-1] != '.' else ip[:-1] # Remove the last dot if it exists
        self.domain_name = domain_name

    def __eq__(self, other):
        if isinstance(other, PTRRecord):
            return (
                    self.ip == other.ip and
                    self.class_ == other.class_ and
                    self.type_ == other.type_ and
                    self.domain_name == other.domain_name
            )

    # Trim every attribute of the class
    def trim(self):
        super().trim()
        self.ip = self.ip.strip()
        self.domain_name = self.domain_name.strip()

    def show(self):
        super().show()
        print(f"ip : {self.ip}")
        print(f"domain name : {self.domain_name}\n")
