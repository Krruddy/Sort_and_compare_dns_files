from project.files.LOOMFile import LOOMFile
from project.logger.Logger import Logger
from project.records import DNSRecords
import re
import os
import sys
import logging
import errno
import dns.zone
import dns.rdatatype
import dns.rdataclass

from project.argumentparser.ArgumentParser import ArgumentParser
from project.comments import Comments
from project.comments import Comment

from project.logger.CustomFormatter import CustomFormatter

from project.records.record import ARecord
from project.records.record import CNAMERecord
from project.records.record import NSRecord
from project.records.record import PTRRecord
from project.records.record import SOARecord

from project.records.records import ARecords
from project.records.records import CNAMERecords
from project.records.records import NSRecords
from project.records.records import PTRRecords
from project.records.records import SOARecords
from project.sorter.Sorter import Sorter
from pathlib import Path


class DNSFile:
    # The constructor takes the name of the file and sets the type of file, the file content, the space before the incrementation value, the incrementation value and the list of DNS entries.
    def __init__(self, path: Path):
        self.logger = Logger()
        self.path = path
        self.is_reverse = self.__find_file_type(self.path)
        self.file_content = self.__set_file_content(self.path)
        self.space_before_incre_value = self.__find_space_before_incre_value(self.file_content[2])
        self.incre_value = self.__find_incre_value(self.file_content[2])
        self.records = DNSRecords(self.is_reverse)
        self.__set_list_of_DNS_records(self.file_content)
        self._LOOM_file = None
        self.records.show_records()

    # a function named __find_file_type that takes the name of the file and returns the type of file (standard DNS or reverse DNS)
    def __find_file_type(self, name_of_file: str, rev_pattern=r"\d{1,3}\.db$"):
        if re.search(rev_pattern, name_of_file) == None:
            return False
        else:
            return True

    # a function named __set_file_content that takes the name of the file and returns the content of the file in a list
    def __set_file_content(self, name_of_file: str):
        file = open(f"{name_of_file}", "r")
        lines = file.readlines()
        file.close()
        return lines

    # a functionn named __find_space_before_incre_value that takes the line containing the value to increment and returns the amount of spaces before the value to increment
    def __find_space_before_incre_value(self, incre_value_line: str):
        amount_of_spaces = incre_value_line.count(' ') - 1
        return amount_of_spaces

    # a function named __find_incre_value that takes the line containing the value to increment and returns the value to increment
    def __find_incre_value(self, incre_value_line: str):
        incre_value = re.findall(r'\d+', incre_value_line)
        if len(incre_value) == 0:
            self.logger.error(f"Could not find the value to increment in {self.path}.")
            self.logger.error(f"Exiting the program.")
            sys.exit(errno.ENOENT)
        elif len(incre_value) > 1:
            self.logger.warning(f"Found more than one value to increment in {self.path}.")
            return int(incre_value[0])
        else:
            return int(incre_value[0])

    def remove_lines_with_pattern(self, file_content, pattern):
        try:
            lines = file_content
            filtered_lines = [line for line in lines if pattern not in line]
            return '\n'.join(filtered_lines)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    # a function named __set_list_of_DNS_records that takes self, the file content and returns a list of DNS entries
    def __set_list_of_DNS_records(self, file_content: list):

        modified_file_content = self.remove_lines_with_pattern(file_content, "$TTL")
        zone = dns.zone.from_text(modified_file_content, origin="", relativize=False, check_origin=False)

        for name, node in zone.nodes.items():
            for rdataset in node.rdatasets:
                for rdata in rdataset:
                    if rdataset.rdtype == 1:  # A
                        current_record = ARecord(server_name=name.to_text(),
                                                 class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                 type_=dns.rdatatype.to_text(rdataset.rdtype), target=rdata.to_text())
                        current_record.show()
                        self.records.A_records.add_record(current_record)
                    elif rdataset.rdtype == 2:  # NS
                        current_record = NSRecord(server_name=name.to_text(),
                                                  class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                  type_=dns.rdatatype.to_text(rdataset.rdtype), target=rdata.to_text())
                        current_record.show()
                        self.records.NS_records.add_record(current_record)
                    elif rdataset.rdtype == 5:  # CNAME
                        current_record = CNAMERecord(alias=name.to_text(),
                                                     class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                     type_=dns.rdatatype.to_text(rdataset.rdtype),
                                                     target=rdata.to_text())
                        current_record.show()
                        self.records.CNAME_records.add_record(current_record)
                    elif rdataset.rdtype == 6:  # SOA
                        current_record = SOARecord(primary_name_server=rdata.mname.to_text(),
                                                   hostmaster=rdata.rname.to_text(), serial=rdata.serial,
                                                   refresh=rdata.refresh, retry=rdata.retry, expire=rdata.expire,
                                                   minimum_ttl=rdata.minimum)
                        current_record.show()
                        self.records.SOA_records.add_record(current_record)
                    elif rdataset.rdtype == 12:  # PTR
                        current_record = PTRRecord(ip=name.to_text(), class_=dns.rdataclass.to_text(rdataset.rdclass),
                                                   type_=dns.rdatatype.to_text(rdataset.rdtype),
                                                   domain_name=rdata.to_text())
                        current_record.show()
                        self.records.PTR_records.add_record(current_record)

    def __seperate_records_and_comments(self, line: str):

        record_and_comment = line.split(";")

        if len(record_and_comment) == 1:
            record = record_and_comment[0]
            comment = None
        else:
            record = record_and_comment[0]
            comment = Comment(record_and_comment[1].replace("\n", "").strip())

        #print comment then print record
        print(f"comment : {record_and_comment}")

        return record, comment

    # a function named increment_incre_value that increments the value to increment
    def increment_incre_value(self):
        if self.records.SOA_records.number_of_records() > 0:
            self.records.SOA_records.records[0].increment_serial()
        else:
            self.logger.error(f"No SOA record found in {self.path}.")
            self.logger.error(f"Exiting the program.")
            sys.exit(errno.ENOENT)

    # a function named delete_duplicate_entries that deletes the duplicate entries
    def delete_duplicate_entries(self):
        self.records.remove_duplicates()

    def sort_DNS_entries(self):
        self.records.sort()

        # a function named reconstruct_file that reconstructs the file with the new incrementation value and the sorted DNS entries

    def reconstruct_file(self):
        # Reconstructs the 2nd line
        reconstructed_line = self.__reconstruct_line(self.space_before_incre_value, self.incre_value)

        # Open the file
        final_DNS_file = self.__create_tmp_file(f"{self.path}")

        # Add the lines to the file that aren't the DNS records
        for index, line in enumerate(self.file_content):
            if index == 2:
                final_DNS_file.write(reconstructed_line)
            elif self.find_ip_in_line(line) == None and self.find_reverse_ip_in_line(line) == None:
                final_DNS_file.write(line)

        output_lines = self.records.output_lines()

        # Add the sorted DNS entries
        for line in output_lines:
            print(line)
            final_DNS_file.write(line)

        # Close the file
        final_DNS_file.close()

        return 0

    def __create_tmp_file(self, name: str):
        try:
            self.logger.info(f"Creating the file {name}.tmp ...")
            return open(f"{name}.tmp", "x")
        except FileExistsError:
            self.logger.warning(f"The file {name}.tmp already exists and is going to be overwritten.")
            # clear the file
            file = open(f"{name}.tmp", "r+")
            file.truncate(0)
            file.close()

            return open(f"{name}.tmp", "w")

    # a function named reconstruct_line that takes the amount of spaces and the incremented value and returns the line
    def __reconstruct_line(self, amount_of_spaces: int, incremented_value: int):
        reconstructed_line = ""
        for i in range(amount_of_spaces):  #(Is there a way to do this in one line ?)
            reconstructed_line += ' '
        reconstructed_line += str(incremented_value) + " ;\n"
        return reconstructed_line

    # a function named replace_file that takes the name of the file and replaces the old file with the new one
    def replace_file(self):
        #os.remove(f"{self.name}")
        if os.path.isfile(f"{self.path}.tmp"):
            os.rename(f"{self.path}", f"{self.path}.old")
            os.rename(f"{self.path}.tmp", f"{self.path}")
        else:
            os.rename(f"{self.path}._after_LOOM.tmp", f"{self.path}")

    def compare_to_LOOM(self, Loom_file: LOOMFile):

        if Loom_file.records.A_records.number_of_records() > 0:
            self.compare_A_to_LOOM(Loom_file)
        if Loom_file.records.CNAME_records.number_of_records() > 0:
            self.compare_CNAME_to_LOOM(Loom_file)
        if Loom_file.records.PTR_records.number_of_records() > 0:
            self.compare_PTR_to_LOOM(Loom_file)

    def compare_A_to_LOOM(self, Loom_file: LOOMFile):

        self.records.trim()

        # Entries that are in the LOOM file but not in the DNS file
        records_not_in_DNS = []

        for LOOM_record in Loom_file.records.A_records.records:
            if LOOM_record not in self.records.A_records.records:
                records_not_in_DNS += [LOOM_record]

        # Entries that have the same ip address but not the same server name
        records_same_ip = []

        for LOOM_record in Loom_file.records.A_records.records:
            if LOOM_record in self.records.A_records.records:
                continue
            else:
                for DNS_record in self.records.A_records.records:
                    if LOOM_record.target == DNS_record.target:
                        records_same_ip += [LOOM_record]

        # Entries that have the same server name but not the same ip address
        records_same_server_name = []

        for LOOM_record in Loom_file.records.A_records.records:
            if LOOM_record in self.records.A_records.records:
                continue
            else:
                for DNS_record in self.records.A_records.records:
                    if LOOM_record.server_name == DNS_record.server_name:
                        records_same_server_name += [LOOM_record]

        # Print the content of the lists
        print(f"Entries that are in the LOOM file but not in the DNS file :")
        for record in records_not_in_DNS:
            print(record.show())

        print(f"Entries that have the same ip address but not the same server name :")
        for record in records_same_ip:
            print(record.show())

        print(f"Entries that have the same server name but not the same ip address :")
        for record in records_same_server_name:
            print(record.show())

        # Ask the user if the DNS entries should be updated to match the LOOM entries.
        for record in records_not_in_DNS:
            print("\n", "-" * 80, "\n")
            if record in records_same_ip:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that translates the name server {record.server_name} to the ip address {record.target} in the LOOM file, is not present in the local DNS file {self.path}.")
                print(
                    "But, the following entry/s is/are present in the local DNS file and translate to the same ip address. \n")

                for line in self.records.A_records.records:
                    if line.target == record.target:
                        line.show()

                for attempt in range(3):
                    answer = input(
                        f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"replacing the entry in local DNS file {self.path} ...")
                        for line in self.records.A_records.records:
                            if line.target == record.target:
                                self.records.A_records.remove_record(line)
                        self.records.A_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break
                    else:
                        print(f"invalide input, please try again.")

            elif record in records_same_server_name:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that makes the ip address {record.target} point to the server {record.server_name} in the LOOM file, is not present in the local DNS file {self.path}.")
                print(f"But, the following entr/s is/are present in the local DNS resovles the same server name.\n")

                for line in self.records.A_records.records:
                    if line.server_name == record.server_name:
                        line.show()

                for attempt in range(3):
                    answer = input(
                        f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"replacing the entry in local DNS file {self.path} ...")
                        for line in self.records.A_records.records:
                            if line.server_name == record.server_name:
                                self.records.A_records.remove_record(line)
                        self.records.A_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break
                    else:
                        print(f"invalide input, please try again.")

            elif record not in records_same_ip and record not in records_same_server_name:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that makes the ip address {record.target} point to the server {record.server_name} in the LOOM file, is not present in the local DNS file {self.path}.")
                print("See the entry below. \n")
                record.show()

                for attempt in range(3):
                    answer = input(f"Would you like to add that entry to the local DNS file {self.path} ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"Adding the entry to the local DNS file {self.path} ...")
                        self.records.A_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break
                    else:
                        print(f"invalide input, please try again.")

        print("\n", "-" * 80, "\n")
        # Show the the records of the DNS file
        self.records.show_records()

    def compare_CNAME_to_LOOM(self, Loom_file: LOOMFile):
        self.records.trim()
        self.LOOM_file.records.trim()

        # Entries that are in the LOOM file but not in the DNS file
        records_not_in_DNS = []

        for LOOM_record in Loom_file.records.CNAME_records.records:
            if LOOM_record not in self.records.CNAME_records.records:
                records_not_in_DNS += [LOOM_record]

        # Entries that have the same alias but not the same target
        records_same_alias = []

        for LOOM_record in Loom_file.records.CNAME_records.records:
            if LOOM_record in self.records.CNAME_records.records:
                continue
            else:
                for DNS_record in self.records.CNAME_records.records:
                    if LOOM_record.alias == DNS_record.alias:
                        records_same_alias += [LOOM_record]

        # Print the content of the lists
        print(f"Entries that are in the LOOM file but not in the DNS file :")
        for record in records_not_in_DNS:
            print(record.show())

        print(f"Entries that have the same alias but not the same target :")
        for record in records_same_alias:
            print(record.show())

        # Ask the user if the DNS entries should be updated to match the LOOM entries.
        for record in records_not_in_DNS:
            print("\n", "-" * 80, "\n")
            if record in records_same_alias:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that makes the alias {record.alias} point to the target {record.target} in the LOOM file, is not present in the local DNS file {self.path}.")
                print(f"But, the following entry/s is/are present in the local DNS resovles the same alias.\n")

                for line in self.records.CNAME_records.records:
                    if line.alias == record.alias:
                        line.show()

                for attempt in range(3):
                    answer = input(
                        f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"replacing the entry in local DNS file {self.path} ...")
                        for line in self.records.CNAME_records.records:
                            if line.alias == record.alias:
                                self.records.CNAME_records.remove_record(line)
                        self.records.CNAME_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break
                    else:
                        print(f"invalide input, please try again.")

            elif record not in records_same_alias:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that makes the alias {record.alias} point to the target {record.target} in the LOOM file, is not present in the local DNS file {self.path}.")
                print(f"See the entry below. \n")
                record.show()

                for attempt in range(3):
                    answer = input(f"Would you like to add that entry to the local DNS file {self.path} ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"Adding the entry to the local DNS file {self.path} ...")
                        self.records.CNAME_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break
                    else:
                        print(f"invalide input, please try again.")

    def compare_PTR_to_LOOM(self, Loom_file: LOOMFile):

        self.records.trim()
        self.LOOM_file.records.trim()

        # Entries that are in the LOOM file but not in the DNS file
        records_not_in_DNS = []

        for LOOM_record in Loom_file.records.PTR_records.records:
            if LOOM_record not in self.records.PTR_records.records:
                records_not_in_DNS += [LOOM_record]

                # Entries that have the same ip address but not the same server name
        records_same_ip = []

        for LOOM_record in Loom_file.records.PTR_records.records:
            if LOOM_record in self.records.PTR_records.records:
                continue
            else:
                for DNS_record in self.records.PTR_records.records:
                    if LOOM_record.ip == DNS_record.ip:
                        records_same_ip += [LOOM_record]

        # Entries that have the same server name but not the same ip address
        records_same_server_name = []

        for LOOM_record in Loom_file.records.PTR_records.records:
            if LOOM_record in self.records.PTR_records.records:
                continue
            else:
                for DNS_record in self.records.PTR_records.records:
                    if LOOM_record.domain_name == DNS_record.domain_name:
                        records_same_server_name += [LOOM_record]

        # Print the content of the lists
        print(f"Entries that are in the LOOM file but not in the DNS file :")
        for record in records_not_in_DNS:
            print(record.show())

        print(f"Entries that have the same ip address but not the same server name :")
        for record in records_same_ip:
            print(record.show())

        print(f"Entries that have the same server name but not the same ip address :")
        for record in records_same_server_name:
            print(record.show())

        # Ask the user if the DNS entries should be updated to match the LOOM entries.
        for record in records_not_in_DNS:
            print("\n", "-" * 80, "\n")
            if record in records_same_ip:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that translates the ip address {record.ip} to the domain name {record.domain_name} in the LOOM file, is not present in the local DNS file {self.path}.")
                print(
                    "But, the following entry/s is/are present in the local DNS file and translate the same ip address\n")

                for line in self.records.PTR_records.records:
                    if line.ip == record.ip:
                        line.show()

                for attempt in range(3):
                    answer = input(
                        f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"replacing the entry in local DNS file {self.path} ...")
                        for line in self.records.PTR_records.records:
                            if line.ip == record.ip:
                                self.records.PTR_records.remove_record(line)
                        self.records.PTR_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break
                    else:
                        print(f"invalide input, please try again.")

            elif record in records_same_server_name:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that translates the ip address {record.ip} to the domain name {record.domain_name} in the LOOM file, is not present in the local DNS file {self.path}.")
                print(f"But, the following entr/s is/are present in the local DNS resovles the same server name.\n")

                for line in self.records.PTR_records.records:
                    if line.domain_name == record.domain_name:
                        line.show()

                for attempt in range(3):
                    answer = input(
                        f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"replacing the entry in local DNS file {self.path} ...")
                        for line in self.records.PTR_records.records:
                            if line.domain_name == record.domain_name:
                                self.records.PTR_records.remove_record(line)
                        self.records.PTR_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break

            elif record not in records_same_ip and record not in records_same_server_name:
                print(f"file: {self.path}\n")
                print(
                    f"The DNS entry that translates the ip address {record.ip} to the domain name {record.domain_name} in the LOOM file, is not present in the local DNS file {self.path}.")
                print("See the entry below. \n")
                record.show()

                for attempt in range(3):
                    answer = input(f"Would you like to add that entry to the local DNS file {self.path} ? (y/N) : ")
                    if answer.lower() == "y":
                        self.logger.info(f"Adding the entry to the local DNS file {self.path} ...")
                        self.records.PTR_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        self.logger.info(f"The entry will not be added to the local DNS file {self.path}.")
                        break
                    else:
                        print(f"invalide input, please try again.")

        print("\n", "-" * 80, "\n")
        # Show the the records of the DNS file
        self.records.show_records()

    def beautify_DNS_entries(self):
        self.records.beautify()

    @property
    def LOOM_file(self):
        return self._LOOM_file

    @LOOM_file.setter
    def LOOM_file(self, Loom_file):
        if isinstance(Loom_file, self.LOOM_file):
            self._LOOM_file = Loom_file
        else:
            raise TypeError("The LOOM file must be an instance of the class LOOM_file.")

    @LOOM_file.deleter
    def LOOM_file(self):
        del self._LOOM_file
