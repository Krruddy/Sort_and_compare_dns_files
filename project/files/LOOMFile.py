import re
import os

from project.main import DNS_records
from project.records.record.ARecord import ARecord
from project.records.record.CNAMERecord import CNAMERecord
from project.records.record.PTRRecord import PTRRecord


class LOOMFile:

    def __init__(self, path: str, DNS_file=None):
        if os.path.isfile(path + "/" + DNS_file.path):
            self._DNS_file = DNS_file
            self.path = path
            self.name = self._DNS_file.path
            self.is_reverse = self._DNS_file.is_reverse
            self.file_content = self.__set_file_content(self.name, self.path)
            self.records = DNS_records()
            self.list_of_DNS_records = self.__set_list_of_DNS_records(self.file_content)

        else:
            raise FileNotFoundError

    def __set_file_content(self, name: str, path: str):
        file = open(f"{path}/{name}", "r")
        lines = file.readlines()
        file.close()
        return lines

    def __set_list_of_DNS_records(self, file_content: list):
        for line in file_content.copy():
            # Empty lines
            if len(line.split()) > 0:
                # Comments
                if line.strip()[0] != ";":
                    if self.find_ip_in_line(line) != None:  # A, AAAA
                        if line.split()[2] == "A":

                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = ARecord(server_name=line_without_comment.split()[0],
                                                     class_=line_without_comment.split()[1],
                                                     type_=line_without_comment.split()[2],
                                                     target=line_without_comment.split()[3])

                            self.records.A_records.add_record(current_record)

                        elif line.split()[2] == "AAAA":
                            pass
                    elif self.find_reverse_ip_in_line(line) != None:  # PTR
                        if line.split()[2] == "PTR":
                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = PTRRecord(ip=line_without_comment.split()[0],
                                                       class_=line_without_comment.split()[1],
                                                       type_=line_without_comment.split()[2],
                                                       domain_name=line_without_comment.split()[3])
                            self.records.PTR_records.add_record(current_record)

                    elif len(line.split()) >= 4:  # Other records
                        if line.split()[2] == "CNAME":

                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = CNAMERecord(alias=line_without_comment.split()[0],
                                                         class_=line_without_comment.split()[1],
                                                         type_=line_without_comment.split()[2],
                                                         target=line_without_comment.split()[3])
                            self.records.CNAME_records.add_record(current_record)
                        elif line.split()[2] == "MX":
                            pass
                    else:
                        pass  #raise UnkownRecordType

    def find_ip_in_line(self, line: str, ip_pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?=[ ;]|$)"):
        match = re.search(ip_pattern, line)
        return match

    # a function named find_reverse_ip_in_line that determines if there is a reverse ip address in the line and returns the match
    def find_reverse_ip_in_line(self, line: str, ip_pattern=r"\d{1,3}\.\d{1,3}"):
        match = re.search(ip_pattern, line)
        return match

    def __seperate_records_and_comments(self, line: str):

        record_and_comment = line.split(";")

        #print comment then print record
        print(f"comment : {record_and_comment}")

        if len(record_and_comment) == 1:
            return record_and_comment[0]
        else:
            comment = record_and_comment[1]  #unused for now
            return record_and_comment[0]

    def show_records(self):
        self.records.show_records()

    @property
    def DNS_file(self):
        return self._DNS_file

    @DNS_file.setter
    def DNS_file(self, DNS_file):
        if isinstance(DNS_file, DNS_file):
            self._DNS_file = DNS_file
        else:
            raise TypeError("The DNS file must be an instance of the class DNS_file.")

    @DNS_file.deleter
    def DNS_file(self):
        del self._DNS_file
