import re
import ipaddress
import os
import sys
import logging
import errno
import filecmp  

manual_LOOM_path = "/home/ruddy/github/Sort_and_compare_dns_files/LOOM"

"""
This program increments the number of line 3, removes the duplicates and sorts based on IP addresses the DNS entries. 
This program does not delete the old file, it renames it with the extension ".old" and creates a new file with the same name as the old one.
For the program to work, the following conditions must be met:
- The file must only contain A records (the other records will be ignored).
- The number that has to be incremented must be in the third line of the file.
- The only ip addresses present in the standard DNS file must be part of the DNS entries. 
- The only ip addresses (with the patern "XXX.XXX") present in the reverse DNS must be part of the DNS entries.
- The name of the reverse DNS file must look like this "XXX.XXX.db" otherwise the program will consider it as a standard DNS file.
The second part of this program is going to compare the DNS file provided with the DNS file present in the "LOOM" directory.
For this part of the program to work, the following conditions must be met:
- nothing different from the conditions above.
- If possible no comments in the DNS files.
"""

# raised when the entries in the DNS file and the LOOM file are identical
class IdenticalEntries(Exception):  
    pass

class NoChangesMade(Exception):
    pass

class UnkownRecordType(Exception):
    pass


# Custom formatter class
class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: "[+] %(message)s",
        logging.WARNING: "[!] %(message)s",
        logging.ERROR: "[-] %(message)s",
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno, self._style._fmt)
        self._style._fmt = log_format
        return super().format(record)

# Create a logger
logger = logging.getLogger("my_logger")

# Create a StreamHandler and set the custom formatter
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())

# Add the handler to the logger
logger.addHandler(handler)

# Set the logging level
logger.setLevel(logging.INFO)

class Record:
    def __init__ (self, TTL: int = None, class_: str = "IN", type_: str = None, comment: str = ""):
        self.TTL = TTL
        self.class_ = class_
        self.type_ = type_
        self.comment = comment
        
    def show(self):
        print(f"TTL : {self.TTL}")
        print(f"class : {self.class_}")
        print(f"type : {self.type_}")
        print(f"comment : {self.comment}")
     
class A_record(Record):
    def __init__ (self, server_name: str, TTL: int = None, class_: str = "IN", type_: str = "A", target: str = None, comment: str = ""):
        super().__init__(TTL, class_, type_, comment)
        self.server_name = server_name
        self.target = target
        
    def __eq__(self, other):
        if isinstance(other, A_record):
            return (
                self.server_name == other.server_name and
                self.class_ == other.class_ and
                self.type_ == other.type_ and
                self.target == other.target
            )
        
    # Trim every attribute of the class
    def trim(self):
        self.server_name = self.server_name.strip()
        self.class_ = self.class_.strip()
        self.type_ = self.type_.strip()
        self.target = self.target.strip()
        self.comment = self.comment.strip()
        
    def show(self):
        super().show()
        print(f"server name : {self.server_name}")
        print(f"target : {self.target}\n")

class CNAME_record(Record):
    def __init__ (self, domain_name: str, TTL: int = None, class_: str = "IN", type_: str = "CNAME", target: str = None, comment: str = ""):
        super().__init__(TTL, class_, type_, comment)
        self.domain_name = domain_name
        self.target = target
        
    def __eq__(self, other):
        if isinstance(other, CNAME_record):
            return (
                self.domain_name == other.domain_name and
                self.class_ == other.class_ and
                self.type_ == other.type_ and
                self.target == other.target
            )

    # Trim every attribute of the class
    def trim(self):
        self.domain_name = self.domain_name.strip()
        self.class_ = self.class_.strip()
        self.type_ = self.type_.strip()
        self.target = self.target.strip()
        self.comment = self.comment.strip()

    def show(self):
        super().show()
        print(f"domain name : {self.domain_name}")
        print(f"target : {self.target}\n")
                
class PTR_record(Record):
    def __init__ (self, ip: str, TTL: int = None, class_: str = "IN", type_: str = "PTR", domain_name: str = None, comment: str = ""):
        super().__init__(TTL, class_, type_, comment)
        self.ip = ip
        self.domain_name = domain_name

    # Trim every attribute of the class
    def trim(self):
        self.ip = self.ip.strip()
        self.class_ = self.class_.strip()
        self.type_ = self.type_.strip()
        self.domain_name = self.domain_name.strip()
        self.comment = self.comment.strip()
    
    def __eq__(self, other):
        if isinstance(other, PTR_record):
            return (
                self.ip == other.ip and
                self.class_ == other.class_ and
                self.type_ == other.type_ and
                self.domain_name == other.domain_name
            )
    
    def show(self):
        super().show()
        print(f"ip : {self.ip}")
        print(f"domain name : {self.domain_name}\n")
        
class DNS_records:
 
    def __init__(self, reverse: bool = False):
        self.is_reverse = reverse
        self.records = {
            "A": [],
            "AAAA": [],
            "CNAME": [],
            "PTR": [],
        }
  
    def set_reverse(self, reverse: bool):
        self.is_reverse = reverse
        
    def add_record(self, record: Record):
        self.records[record.type_] += [record]
        
    def remove_record(self, record: Record):
        self.records[record.type_].remove(record)
    
    def __eq__(self, other):
        if isinstance(other, DNS_records):
            return (
                self.records == other.records
            )
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def simple_compare(self, left, right): 
        if isinstance(left, A_record) and isinstance(right, A_record):
            if left.type_ == right.type_ == "A":
                return self.simple_compare_A(left, right)
            elif left.type_ == right.type_ == "CNAME":
                return self.simple_compare_CNAME(left, right)
            elif left.type_ == right.type_ == "PTR":
                return self.simple_compare_PTR(left, right)
                
    def simple_compare_A(self, left, right):
        if isinstance(left, A_record) and isinstance(right, A_record):
            return (left.server_name == right.server_name 
                and left.class_ == right.class_
                and left.type_ == right.type_
                and left.target == right.target)
            
    def simple_compare_CNAME(self, left, right):
        if isinstance(left, CNAME_record) and isinstance(right, CNAME_record):
            return (left.domain_name == right.domain_name 
                and left.class_ == right.class_
                and left.type_ == right.type_
                and left.target == right.target)
    
    def simple_compare_PTR(self, left, right):
        if isinstance(left, PTR_record) and isinstance(right, PTR_record):
            return (left.ip == right.ip 
                and left.class_ == right.class_
                and left.type_ == right.type_
                and left.domain_name == right.domain_name)
          
    def show_records(self):
        for record_type in self.records:
            print(f"Records of type {record_type} :")
            for record in self.records[record_type]:
                record.show()
                print("\n")
             
    def show_records_of_type(self, record_type: str):
        for record in self.records[record_type]:
            record.show()
            print("\n")
    
    def show_number_of_records(self):
        for record_type in self.records:
            print(f"Number of records of type {record_type} : {len(self.records[record_type])}")
          
    def number_of_records_of_type(self, record_type: str):
        return len(self.records[record_type])
                
    def beautify (self):
        if not self.is_reverse:
            self.beautify_standard()
        else:
            self.beautify_reverse()                
    
    def beautify_standard(self):
        for record_type in self.records:
            if len(self.records[record_type]) > 0:

                if not self.is_reverse:
                    longest_element = max([len(record.server_name) for record in self.records[record_type]])
                    for record in self.records[record_type]:
                        added_spaces = longest_element - len(record.server_name)+1
                        record.server_name += " " * added_spaces
                        record.class_ += " " * 6
                        record.type_ += " " * 7 

    def beautify_reverse(self):
        for record_type in self.records:
            if len(self.records[record_type]) > 0:

                if self.is_reverse:
                    longest_element = max([len(record.ip) for record in self.records[record_type]])
                    for record in self.records[record_type]:
                        added_spaces = longest_element - len(record.ip)+1
                        record.ip += " " * added_spaces
                        record.class_ += " " * 6
                        record.type_ += " " * 7
    
    def remove_duplicates(self):
        if not self.is_reverse:
            self.remove_standard_duplicates()
        else:
            self.remove_reverse_duplicates() 
        
    def remove_standard_duplicates(self):
        for record_type in self.records:
            seen = set()
            self.records[record_type] = [x for x in self.records[record_type] if not (x.server_name in seen or seen.add(x.server_name))]
        
    def remove_reverse_duplicates(self):
        for record_type in self.records:
            seen = set()
            self.records[record_type] = [x for x in self.records[record_type] if not (x.ip in seen or seen.add(x.ip))]
 
    def sort(self):
        if not self.is_reverse:
            self.sort_standard()
        else:
            self.sort_reverse()
            
    def sort_standard(self, by: str = "server_name"):
        for record_type in self.records:
            self.records[record_type].sort(key=lambda x: getattr(x, by))
    
    def sort_reverse(self, by: str = "ip"):
        for record_type in self.records:
            self.records[record_type].sort(key=lambda x: list(map(int, getattr(x, by).split('.'))))   
    
    def trim(self):
        for record_type in self.records:
            for record in self.records[record_type]:
                record.trim()
    
    def output_lines(self):
        lines = []
        for record_type in self.records:
            for record in self.records[record_type]:
                if record_type == "A":
                    lines += [record.server_name + record.class_ + record.type_ + record.target + "\n"]
                if record_type == "CNAME":
                    lines += [record.domain_name + record.class_ + record.type_ + record.target + "\n"]
                if record_type == "PTR":
                    lines += [record.ip + record.class_ + record.type_ + record.domain_name + "\n"]
        return lines
            
class Comments:
    def __init__(self):
        self.comments = []
    def add_comment(self, comment: str):
        self.comments += [comment]
    def remove_comment(self, comment: str):
        self.comments.remove(comment)
    def show_comments(self):
        for comment in self.comments:
            print(comment)
            print("\n")
        
class LOOM_file:
    
    def __init__(self, path: str, DNS_file = None):
        if os.path.isfile(path+"/"+DNS_file.name):
            self._DNS_file = DNS_file
            self.path = path
            self.name = self._DNS_file.name
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
        for line in file_content:
            # Empty lines
            if len(line.split()) > 0:
                # Comments
                if line.strip()[0] != ";":
                    if self.find_ip_in_line(line) != None: # A, AAAA
                        print(f"a comment is being added for line {line}")
                        if line.split()[2] == "A":
                            
                            current_record = A_record(server_name = line.split()[0], class_ = line.split()[1], type_ = line.split()[2], target = line.split()[3])
                            print(f"length of line is {len(line.split())}")
                            
                            self.records.add_record(current_record)
                            
                        elif line.split()[2] == "AAAA":
                            pass
                    elif self.find_reverse_ip_in_line(line) != None: # PTR
                        if line.split()[2] == "PTR":
                            print(f"PTR record {line}")
                            current_record = PTR_record(ip = line.split()[0], class_ = line.split()[1], type_ = line.split()[2], domain_name = line.split()[3])
                            self.records.add_record(current_record)
                        
                    elif len(line.split()) > 4: # Other records
                        if line.split()[2] == "CNAME":
                            
                            current_record = CNAME_record(domain_name = line.split()[0], class_ = line.split()[1], type_ = line.split()[2], target = line.split()[3])
                            self.records.add_record(current_record)

                        elif line.split()[2] == "MX":
                            pass
                    else:
                        pass #raise UnkownRecordType

    def find_ip_in_line(self, line: str, ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?=[ ;]|$)"):
        match = re.search(ip_pattern, line)
        return match
    
    # a function named find_reverse_ip_in_line that determines if there is a reverse ip address in the line and returns the match
    def find_reverse_ip_in_line(self, line: str, ip_pattern = r"\d{1,3}\.\d{1,3}"):
        match = re.search(ip_pattern, line)
        return match

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
        
# a class named DNS_file that takes the name of the file.
class DNS_file:
    # The constructor takes the name of the file and sets the type of file, the file content, the space before the incrementation value, the incrementation value and the list of DNS entries.
    def __init__(self, name: str): 
        self.name = name
        self.is_reverse = self.__find_file_type(self.name)
        self.file_content = self.__set_file_content(self.name)
        self.space_before_incre_value = self.__find_space_before_incre_value(self.file_content[2])
        self.incre_value = self.__find_incre_value(self.file_content[2])
        self.records = DNS_records(self.is_reverse)
        self.list_of_DNS_records = self.__set_list_of_DNS_records(self.file_content)
        self._LOOM_file = None
        print("#"*300)
        self.records.show_records()
        self.comments = self.__set_comments(self.file_content)

    # a function named __find_file_type that takes the name of the file and returns the type of file (standard DNS or reverse DNS)      
    def __find_file_type(self, name_of_file: str, rev_pattern = r"\d{1,3}\.db$"):
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
            logger.error(f"Could not find the value to increment in {self.name}.")
            logger.error(f"Exiting the program.")
            sys.exit(errno.ENOENT)
        elif len(incre_value) > 1:
            logger.warning(f"Found more than one value to increment in {self.name}.")
            return int(incre_value[0])
        else:
            return int(incre_value[0])

    # a function named __set_list_of_DNS_records that takes self, the file content and returns a list of DNS entries    
    def __set_list_of_DNS_records(self, file_content: list):
        
        for line in file_content:
            # Empty lines
            if len(line.split()) > 0:
                # Comments
                if line.strip()[0] != ";":
                    if self.find_ip_in_line(line) != None: # A, AAAA
                        print(f"a comment is being added for line {line}")
                        if line.split()[2] == "A":
                            
                            current_record = A_record(server_name = line.split()[0], class_ = line.split()[1], type_ = line.split()[2], target = line.split()[3])
                            print(f"length of line is {len(line.split())}")
                            
                            self.records.add_record(current_record)
                            
                        elif line.split()[2] == "AAAA":
                            pass
                    elif self.find_reverse_ip_in_line(line) != None: # PTR
                        if line.split()[2] == "PTR":
                            print(f"PTR record {line}")
                            current_record = PTR_record(ip = line.split()[0], class_ = line.split()[1], type_ = line.split()[2], domain_name = line.split()[3])
                            self.records.add_record(current_record)
                        
                    elif len(line.split()) > 4: # Other records
                        if line.split()[2] == "CNAME":
                            
                            current_record = CNAME_record(domain_name = line.split()[0], class_ = line.split()[1], type_ = line.split()[2], target = line.split()[3])
                            self.records.add_record(current_record)

                        elif line.split()[2] == "MX":
                            pass
                    else:
                        pass #raise UnkownRecordType
                                                            
    # a function named find_ip_in_line that determines if there is an ip address in the line and returns the match
    def find_ip_in_line(self, line: str, ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?=[ ;]|$)"):
        match = re.search(ip_pattern, line)
        return match
    
    # a function named find_reverse_ip_in_line that determines if there is a reverse ip address in the line and returns the match
    def find_reverse_ip_in_line(self, line: str, ip_pattern = r"\d{1,3}\.\d{1,3}"):
        match = re.search(ip_pattern, line)
        return match

    def __set_comments(self, file_content: list):
        return 0
   
    # a function named increment_incre_value that increments the value to increment
    def increment_incre_value(self):
        self.incre_value += 1
    
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
        final_DNS_file = self.__create_tmp_file(f"{self.name}")
        
        
        # Add the lines to the file that aren't the DNS entries
        for index, line in enumerate(self.file_content):
            if  index == 2:
                final_DNS_file.write(reconstructed_line)
            elif self.find_ip_in_line(line) == None and self.find_reverse_ip_in_line(line) == None:
                final_DNS_file.write(line)
        
        output_lines = self.records.output_lines()
        
        # Add the sorted DNS entries
        for line in output_lines:
            final_DNS_file.write(line)
            
        # Close the file
        final_DNS_file.close()
        
        return 0
    
    def __create_tmp_file(self, name: str):
        try:
            logger.info(f"Creating the file {name}.tmp ...")
            return open(f"{name}.tmp", "x")
        except FileExistsError:
            logger.warning(f"The file {name}.tmp already exists and is going to be overwritten.")
            # clear the file
            file = open(f"{name}.tmp","r+")
            file.truncate(0)
            file.close()
            
            return open(f"{name}.tmp", "w")

    # a function named reconstruct_line that takes the amount of spaces and the incremented value and returns the line
    def __reconstruct_line(self, amount_of_spaces: int, incremented_value: int):
        reconstructed_line = ""
        for i in range(amount_of_spaces): #(Is there a way to do this in one line ?)
            reconstructed_line+=' '
        reconstructed_line += str(incremented_value) + " ;\n"
        return reconstructed_line
     
    # a function named replace_file that takes the name of the file and replaces the old file with the new one
    def replace_file(self):
        #os.remove(f"{self.name}")
        if os.path.isfile(f"{self.name}.tmp"):
            os.rename(f"{self.name}", f"{self.name}.old")
            os.rename(f"{self.name}.tmp", f"{self.name}")
            print('')
        else:
            os.rename(f"{self.name}._after_LOOM.tmp", f"{self.name}")
            print('')

    def compare_to_LOOM(self, Loom_file: LOOM_file):
        
        if Loom_file.records.number_of_records_of_type("A") > 0:
            self.compare_A_to_LOOM(Loom_file)
        if Loom_file.records.number_of_records_of_type("PTR") > 0:
            self.compare_PTR_to_LOOM(Loom_file)
    
    def compare_PTR_to_LOOM(self, Loom_file: LOOM_file):
        
        self.records.trim()
        self.LOOM_file.records.trim()
        
        # Entries that are in the LOOM file but not in the DNS file
        records_not_in_DNS = []
        
        for LOOM_record in Loom_file.records.records["PTR"]:
            if LOOM_record not in self.records.records["PTR"]:
                records_not_in_DNS += [LOOM_record]
                
                
                
        # Entries that have the same ip address but not the same server name
        records_same_ip = []
        
        for LOOM_record in Loom_file.records.records["PTR"]:
            if LOOM_record in self.records.records["PTR"]:
                continue
            else:
                for DNS_record in self.records.records["PTR"]:
                    if LOOM_record.ip == DNS_record.ip:
                        records_same_ip += [LOOM_record]
                        
        # Entries that have the same server name but not the same ip address
        records_same_server_name = []
        
        for LOOM_record in Loom_file.records.records["PTR"]:
            if LOOM_record in self.records.records["PTR"]:
                continue
            else:
                for DNS_record in self.records.records["PTR"]:
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
                print(f"file: {self.name}\n")
                print(f"The DNS entry that translates the ip address {record.ip} to the domain name {record.domain_name} in the LOOM file, is not present in the local DNS file {self.name}.")
                print("But, the following entry/s is/are present in the local DNS file and translate the same ip address\n")
                
                for line in self.records.records["PTR"]:
                    if line.ip == record.ip:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.records["PTR"]:
                            if line.ip == record.ip:
                                self.records.remove_record(line)
                        self.records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
                    else:
                        print(f"invalide input, please try again.")
                        
            elif record in records_same_server_name:
                print(f"file: {self.name}\n")
                print(f"The DNS entry that translates the ip address {record.ip} to the domain name {record.domain_name} in the LOOM file, is not present in the local DNS file {self.name}.")
                print(f"But, the following entr/s is/are present in the local DNS resovles the same server name.\n")
                
                for line in self.records.records["PTR"]:
                    if line.domain_name == record.domain_name:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.records["PTR"]:
                            if line.domain_name == record.domain_name:
                                self.records.remove_record(line)
                        self.records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
        
            elif record not in records_same_ip and record not in records_same_server_name:
                print(f"file: {self.name}\n")
                print(f"The DNS entry that translates the ip address {record.ip} to the domain name {record.domain_name} in the LOOM file, is not present in the local DNS file {self.name}.")
                print("See the entry below. \n")
                record.show()
                
                for attempt in range(3):
                    answer = input(f"Would you like to add that entry to the local DNS file {self.name} ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"Adding the entry to the local DNS file {self.name} ...")
                        self.records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
                    else:
                        print(f"invalide input, please try again.")
                        
        print("\n", "-" * 80, "\n")
        # Show the the records of the DNS file
        self.records.show_records()       
    
    def compare_A_to_LOOM(self, Loom_file: LOOM_file):
        
        self.records.trim()
        
        # Entries that are in the LOOM file but not in the DNS file
        records_not_in_DNS = []
        
        for LOOM_record in Loom_file.records.records["A"]:
            if LOOM_record not in self.records.records["A"]:
                records_not_in_DNS += [LOOM_record]
                
        # Entries that have the same ip address but not the same server name
        records_same_ip = []
        
        for LOOM_record in Loom_file.records.records["A"]:
            if LOOM_record in self.records.records["A"]:
                continue
            else:
                for DNS_record in self.records.records["A"]:
                    if LOOM_record.target == DNS_record.target:
                        records_same_ip += [LOOM_record]
                        
        # Entries that have the same server name but not the same ip address
        records_same_server_name = []
        
        for LOOM_record in Loom_file.records.records["A"]:
            if LOOM_record in self.records.records["A"]:
                continue
            else:
                for DNS_record in self.records.records["A"]:
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
                print(f"file: {self.name}\n")
                print(f"The DNS entry that translates the name server {record.server_name} to the ip address {record.target} in the LOOM file, is not present in the local DNS file {self.name}.")
                print("But, the following entry/s is/are present in the local DNS file and translate to the same ip address. \n")
                
                for line in self.records.records["A"]:
                    if line.target == record.target:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.records["A"]:
                            if line.target == record.target:
                                self.records.remove_record(line)
                        self.records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
                    else:
                        print(f"invalide input, please try again.")
                        
            elif record in records_same_server_name:
                print(f"file: {self.name}\n")
                print(f"The DNS entry that makes the ip address {record.target} point to the server {record.server_name} in the LOOM file, is not present in the local DNS file {self.name}.")
                print(f"But, the following entr/s is/are present in the local DNS resovles the same server name.\n")
                
                for line in self.records.records["A"]:
                    if line.server_name == record.server_name:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.records["A"]:
                            if line.server_name == record.server_name:
                                self.records.remove_record(line)
                        self.records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
                    else:
                        print(f"invalide input, please try again.")
                        
            elif record not in records_same_ip and record not in records_same_server_name:
                print(f"file: {self.name}\n")
                print(f"The DNS entry that makes the ip address {record.target} point to the server {record.server_name} in the LOOM file, is not present in the local DNS file {self.name}.")
                print("See the entry below. \n")
                record.show()
                
                for attempt in range(3):
                    answer = input(f"Would you like to add that entry to the local DNS file {self.name} ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"Adding the entry to the local DNS file {self.name} ...")
                        self.records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
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
        if isinstance(Loom_file, LOOM_file):
            self._LOOM_file = Loom_file
        else:
            raise TypeError("The LOOM file must be an instance of the class LOOM_file.")
        
    @LOOM_file.deleter
    def LOOM_file(self):
        del self._LOOM_file
         
def parse_arguments():
    logger.info("Parsing the arguments ...")
    if len(sys.argv) == 1:
        logger.error(f"No arguments have been passed.")
        logger.error(f"Exiting the program.")
        sys.exit(errno.ENOENT)
    else:
        if "--help" in sys.argv or "-h" in sys.argv:
            print(f"Here are an examples of how to use this program :\n")
            print(f"python3 dns_sorting.py dnsfile.db \n")
            print(f"python3 dns_sorting.py dnsfile.db 10.10.db\n")
            print(f"python3 dns_sorting.py --LOOM_path /home/ruddy/Documents/LOOM/ dnsfile.db 10.10.db\n")
            print("-" * 80)
            print("exiting the program ...")
            sys.exit(0)
        elif "--LOOM_path" in sys.argv:
            if len(sys.argv) <= 3:
                logger.error(f"No file has been passed as an argument.")
                logger.error(f"Exiting the program.")
                sys.exit(errno.ENOENT)
            else:    
                LOOM_path = sys.argv[sys.argv.index("--LOOM_path") + 1]
                logger.info(f"The path to the LOOM directory is {LOOM_path}.")
        else:
            LOOM_path = None
            logger.warning(f"The path to the LOOM directory is not specified, using the path predefined in the program.")
            
        # populates the list of DNS_files
        DNS_files = []
        logger.info(f"Populating the DNS list ...")
        for index, argument in enumerate(sys.argv):
            if argument == "--LOOM_path" or sys.argv[index - 1] == "--LOOM_path":
                continue
            elif index != 0:
                logger.info(f"adding {argument} to the list of DNS files ...")
                DNS_files += [DNS_file(argument)]
                print(f"-" * 80)
        
        return DNS_files, LOOM_path
    
logger.info("Starting the program.")

DNS_files, LOOM_path = parse_arguments()

if LOOM_path == None:
    LOOM_path = manual_LOOM_path
                        
# increments the value to increment, deletes the duplicate entries, sorts the DNS entries, reconstructs the file and replaces the old file with the new one
for file in DNS_files:
    logger.info(f"incrementing the value for {file.name} ...")
    file.increment_incre_value()
    logger.info(f"deleting the duplicate entries for {file.name} ...")
    file.beautify_DNS_entries()
    file.delete_duplicate_entries()
    logger.info(f"sorting the DNS entries for {file.name} ...")
    file.sort_DNS_entries()
    logger.info(f"reconstructing the file {file.name} ...")
    file.reconstruct_file()
    logger.info(f"replacing the old file with the new one for {file.name} ...")
    file.replace_file()
    print(f"-" * 80)
    
###################################
# The file comparison starts here #
###################################
print(f"\n" * 2)
print(f"#" * 32)
print(f"# Starting the file comparison #")
print(f"#" * 32, "\n\n")
print(f"\n" * 2)

if os.path.isdir(f"{LOOM_path}") == False:
    logger.error(f"The path {LOOM_path} is not valid.")
    logger.error(f"The comparison between the DNS files and the LOOM files cannot be done.")
    logger.error(f"Exiting the program.")
    sys.exit(errno.ENOENT)



LOOM_files = []

# instantiate the LOOM files
for file in DNS_files:
    try:
        Loom_file = LOOM_file(LOOM_path, file)
        LOOM_files += [Loom_file]
        file.LOOM_file = Loom_file
        
    except FileNotFoundError:
        print(f"-" * 80)
        continue

for file in DNS_files:
    print(f"-" * 80)
    print(f"Comparing the DNS file {file.name} with the LOOM file {file.LOOM_file.name} ...")
    file.compare_to_LOOM(file.LOOM_file)
    print(f"-" * 80)
    file.beautify_DNS_entries()
    file.reconstruct_file()
    file.replace_file()

#LOOM_files[0].show_records()

if False:
    #define the path to the LOOM directory and check if it exists

    for file in DNS_files:
        try:
            logger.info(f"Setting up the LOOM configuration for {file.name} ...")
            file.setup_LOOM_config(LOOM_path)
        except FileNotFoundError:
            print(f"-" * 80)
            continue
        logger.info(f"Looking for duplicates in the LOOM file {file.LOOM_file_path} ...")
        file.delete_duplicate_entries(LOOM = True)
        # It's useless to sort the content of the variable that contains the LOOM file content because it's not going to be written to the file.
        #logger.info(f"Attempting to sort the LOOM file {file.LOOM_file_path} ...")
        #file.sort_DNS_entries(LOOM = True)
        try:
            logger.info(f"Comparing the DNS entries of the file {file.name} with the LOOM file {file.LOOM_file_path} ...")
            file.compare_DNS_entries()
        except (IdenticalEntries, NoChangesMade):
            print(f"-" * 80)
            continue
        file.sort_DNS_entries(LOOM = True)
        logger.info(f"reconstructing the file {file.name} with the added entries to the DNS file ...") 
        file.beautify_DNS_entries()
        file.reconstruct_file(LOOM = True)
        logger.info(f"replacing the old file with the new one for {file.name} ...")
        file.replace_file()
        print(f"-" * 80)

logger.info("The program has finished running.")


# Should I add Docstrings ?
# Add a function that checks if all of the DNS entries are of type A (read the 3rd word of the lines that contain an ip address).
# Have None instead of having objects with missing attributes.
# Sort and delete duplicates in the object that represents the LOOM file, but don't write it to the file.
# if there are duplicates in LOOM warn the user.
# After having asked for the changes to the user, do a last check between the DNS file and the LOOM file. then if they aren't the same warn the user.
#have an __str__ method for the DNS_file class.
# hanfdle comments in the DNS files dictionary key=line, value=comment
# In the DNS files, there are duplicate entries that don't have the same tabulation. So instead of calling it beautify, you should call it normalize. Or changing the way the entries are stored. make it so that they are stored as disctionaries or pairs that way you can very easily sort and remove duplicates
# handle entries that have the same server name but not the same ip address
# add a type that is a list of DNS RECORDS so that they sort themselves and remove duplicates based on theire type.
# move simple_compare_PTR to the records themselves instead of the records class.
