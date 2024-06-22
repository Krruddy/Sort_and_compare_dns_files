from project.records.record.AbstractRecord import AbstractRecord


class NSAbstractRecord(AbstractRecord):

    def __init__ (self, server_name: str, TTL: int = None, class_: str = "IN", type_: str = "NS", target: str = None, comment = None):
        super().__init__(TTL, class_, type_, comment)
        self.server_name = server_name
        self.target = target


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
        if self.comment == None:
            return f"{self.TTL} {self.class_} {self.type_} {self.server_name}."
        else:
            return f"{self.TTL} {self.class_} {self.type_} {self.server_name}. ; {self.comment.get()}"

