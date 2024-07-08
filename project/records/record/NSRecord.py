from project.records.record.AbstractRecord import AbstractRecord


class NSRecord(AbstractRecord):

    def __init__(self, server_name: str, TTL: int = 56746, class_: str = "IN", type_: str = "NS", target: str = None, zone:str = None ,comment=None):
        super().__init__(TTL, class_, type_, comment)
        self.server_name = server_name
        self.target = target
        self.zone = zone

    # Trim every attribute of the class
    def trim(self):
        super().trim()
        self.server_name = self.server_name.strip()
        self.target = self.target.strip()

    def show(self):
        super().show()
        print(f"server name : {self.server_name}")
        print(f"target : {self.target}\n")

    def generate_output(self):
        if self.zone == '.':
            return f"\t{self.TTL}\t{self.class_}\t{self.type_}\t{self.target}"
        else:
            self.zone = self.zone[:-1] if self.zone[-1] == '.' else self.zone
            return f"{self.zone}\t{self.class_}\t{self.type_}\t{self.target}"
