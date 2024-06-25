from enum import Enum

class RecordType(Enum):
    A = 1
    NS = 2
    CNAME = 5
    SOA = 6
    PTR = 12