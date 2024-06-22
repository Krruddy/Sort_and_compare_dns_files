from project.records.record.AbstractRecord import AbstractRecord

class SOARecord(AbstractRecord):

    def __init__ (self, primary_name_server: str, hostmaster: str, serial: int, refresh: int, retry: int, expire: int, minimum_ttl: int):
        super().__init__(minimum_ttl, "IN", "SOA")
        self.primary_name_server = primary_name_server
        self.hostmaster = hostmaster
        self.serial = serial
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.minimum_ttl = minimum_ttl

    def increment_serial(self):
        self.serial += 1

    def show(self):
        super().show()
        print(f"primary name server : {self.primary_name_server}")
        print(f"hostmaster : {self.hostmaster}")
        print(f"serial : {self.serial}")
        print(f"refresh : {self.refresh}")
        print(f"retry : {self.retry}")
        print(f"expire : {self.expire}")
        print(f"minimum TTL : {self.minimum_ttl}\n")

    def generate_output(self):

        line = f"""
        @       IN     SOA     {self.primary_name_server}. {self.hostmaster}. (
                {self.serial}
                {self.refresh}
                {self.retry}
                {self.expire}
                {self.minimum_ttl}
        )
        """

        return line