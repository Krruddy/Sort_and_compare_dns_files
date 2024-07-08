from project.records.record.AbstractRecord import AbstractRecord

class SOARecord(AbstractRecord):
    TIME_UNITS = {
        '1d': 86400,  # 1 day in seconds
        '1h': 3600,   # 1 hour in seconds
        '1w': 604800, # 1 week in seconds
        '1m': 2592000 # 1 month in seconds
    }

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

    def set_record(self, SOA_record):
        self.primary_name_server = SOA_record.primary_name_server
        self.hostmaster = SOA_record.hostmaster
        self.serial = SOA_record.serial
        self.refresh = SOA_record.refresh
        self.retry = SOA_record.retry
        self.expire = SOA_record.expire
        self.minimum_ttl = SOA_record.minimum_ttl

    # TODO find a way to not have the dots at the end of the primary name server and the hostmaster
    def generate_output(self):
        line = f"""
@\tIN\tSOA\t{self.primary_name_server}\t{self.hostmaster} (
\t{self.serial} ;
\t{self.refresh} ;
\t{self.retry} ;
\t{self.expire} ;
\t{self.minimum_ttl} ;
)\n
"""
        return line
