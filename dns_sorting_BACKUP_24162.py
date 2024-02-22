import re
import os
import sys
import logging
import errno

manual_LOOM_path = "/home/ruddy/github/Sort_and_compare_dns_files/LOOM"

"""
This program increments the number on line 3, removes the duplicates and sorts based on IP addresses the DNS entries. 
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

class Comment:
    
    def __init__(self, comment: str, record = None):
        self.comment = comment
        self._record = record
      
    def show(self):
        print(self.comment)
        print("\n")
    
    def get(self):
        return self.comment
    
    def set(self, comment: str):
        self.comment = comment
      
    @property
    def record(self):
        return self._record
    
    @record.setter
    def record(self, record):
        if isinstance(record, Record):
            self._record = record
        if record == None:
            self._record = None
        else:
            raise TypeError("The record must be an instance of the class Record.")
    
class Comments:
    
    def __init__(self):
        self.comments = []
        
    def add_comment(self, comment: Comment):
        self.comments.append(comment)
        
    def remove_comment(self, comment: Comment):
        self.comments.remove(comment)
        
    def show_comments(self):
        for comment in self.comments:
            comment.show()
 
class Record:
    def __init__ (self, TTL: int = None, class_: str = "IN", type_: str = None, comment= None ):
        self.TTL = TTL
        self.class_ = class_
        self.type_ = type_
     
    def trim(self):
        self.class_ = self.class_.strip()
        self.type_ = self.type_.strip()
        
    def show(self):
        print(f"class : {self.class_}")
        print(f"TTL : {self.TTL}")
        print(f"comment : {self.comment}")
        print(f"type : {self.type_}")
     
    @property
    def comment(self):
        return self._comment
    
    @comment.setter
    def comment(self, comment):
        if isinstance(comment, Comment):
            self._comment = comment
        else:
            raise TypeError("The comment must be an instance of the class Comment.")
     
class A_record(Record):
    def __init__ (self, server_name: str, TTL: int = None, class_: str = "IN", type_: str = "A", target: str = None, comment = None):
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
                
    def simple_compare(self, other):
        if isinstance(other, A_record):
            return (self.server_name == other.server_name 
                and self.class_ == other.class_
                and self.type_ == other.type_
                and self.target == other.target)
        else:
            raise TypeError("The object must be an instance of the class A_record.")

    # Trim every attribute of the class
    def trim(self):
        super().trim()
        self.server_name = self.server_name.strip()
        self.target = self.target.strip()

    def show(self):
        super().show()
        print(f"server name : {self.server_name}")
        print(f"target : {self.target}\n")

class CNAME_record(Record):
    def __init__ (self, alias: str, TTL: int = None, class_: str = "IN", type_: str = "CNAME", target: str = None, comment = None):
        super().__init__(TTL, class_, type_, comment)
        self.alias = alias
        self.target = target
        
    def __eq__(self, other):
        if isinstance(other, CNAME_record):
            return (
                self.alias == other.alias and
                self.class_ == other.class_ and
                self.type_ == other.type_ and
                self.target == other.target
            )

    def simple_compare(self, other):
        if isinstance(other, CNAME_record):
            return (self.alias == other.alias 
                and self.class_ == other.class_
                and self.type_ == other.type_
                and self.target == other.target)
        else:
            raise TypeError("The object must be an instance of the class CNAME_record.")
    
    # Trim every attribute of the class
    def trim(self):
        super().trim()
        self.alias = self.alias.strip()
        self.target = self.target.strip()

    def show(self):
        super().show()
        print(f"domain name : {self.alias}")
        print(f"target : {self.target}\n")
                
class PTR_record(Record):
    def __init__ (self, ip: str, TTL: int = None, class_: str = "IN", type_: str = "PTR", domain_name: str = None, comment = None):
        super().__init__(TTL, class_, type_, comment)
        self.ip = ip
        self.domain_name = domain_name

    def __eq__(self, other):
        if isinstance(other, PTR_record):
            return (
                self.ip == other.ip and
                self.class_ == other.class_ and
                self.type_ == other.type_ and
                self.domain_name == other.domain_name
            )

    def simple_compare(self, other):
        if isinstance(other, PTR_record):
            return (self.ip == other.ip 
                and self.class_ == other.class_
                and self.type_ == other.type_
                and self.domain_name == other.domain_name)
        else:
            raise TypeError("The object must be an instance of the class PTR_record.")

    # Trim every attribute of the class
    def trim(self):
        super().trim()
        self.ip = self.ip.strip()
        self.domain_name = self.domain_name.strip()
    
    def show(self):
        super().show()
        print(f"ip : {self.ip}")
        print(f"domain name : {self.domain_name}\n")

class Records:
    
    def __init__(self):
        self.records = []
        
    def add_record(self, record: Record):
        self.records += [record]
    
    def remove_record(self, record: Record):
        self.records.remove(record)
    
    def simple_compare(self, left, right): 
        if isinstance(left, Record) and isinstance(right, Record):
            left.simple_compare(right)
        else:
            raise TypeError("The objects must be instances of the class Record.")
    
    def show_records(self):
        for record in self.records:
            record.show()
            print("\n")
    
    def show_number_of_records(self):
        print(f"Number of records : {len(self.records)}")
    
    def trim(self):
        for record in self.records:
            record.trim()
    
    def number_of_records(self):
        return len(self.records)
            
class A_records(Records):
  
    def __init__(self):
        super().__init__()
        
    def beautify(self):
        if len(self.records) != 0:
            longest_element = max([len(record.server_name) for record in self.records])
            for record in self.records:
                added_spaces = longest_element - len(record.server_name)+1
                record.server_name += " " * added_spaces
                record.class_ += " " * 6
                record.type_ += " " * 7
    
    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.target in seen or seen.add(x.target))]
        
    def sort(self):
        for record in self.records:
            print(record.target)
        self.records.sort(key=lambda x: list(map(int, x.target.split('.'))))

    def output_lines(self):
        lines = []
        for record in self.records:
            lines += [record.server_name + record.class_ + record.type_ + record.target + "\n"]
        return lines
class CNAME_records(Records):
      
    def __init__(self):
        super().__init__()
        
    def beautify(self):
        
        if len(self.records) != 0:
            longest_element = max([len(record.alias) for record in self.records])
            for record in self.records:
                added_spaces = longest_element - len(record.alias)+1
                record.alias += " " * added_spaces
                record.class_ += " " * 6
                record.type_ += " " * 7
    
    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.alias in seen or seen.add(x.alias))]
        
    def sort(self):
        self.records.sort(key=lambda x: x.alias)

    def output_lines(self):
        lines = []
        for record in self.records:
            lines += [record.alias + record.class_ + record.type_ + record.target + "\n"]
        return lines

class PTR_records(Records):
  
    def __init__(self):
        super().__init__()
        
    def beautify(self):
        if len(self.records) != 0:
            longest_element = max([len(record.ip) for record in self.records])
            for record in self.records:
                added_spaces = longest_element - len(record.ip)+1
                record.ip += " " * added_spaces
                record.class_ += " " * 6
                record.type_ += " " * 7
    
    def remove_duplicates(self):
        seen = set()
        self.records = [x for x in self.records if not (x.ip in seen or seen.add(x.ip))]
        
    def sort(self):
        self.records.sort(key=lambda x: list(map(int, x.ip.split('.'))))  
    
    def output_lines(self):
        lines = []
        for record in self.records:
            lines += [record.ip + record.class_ + record.type_ + record.domain_name + "\n"]
        return lines      
      
class DNS_records:
 
    def __init__(self, reverse: bool = False):
        self.is_reverse = reverse
        self.A_records = A_records()
        self.CNAME_records = CNAME_records()
        self.PTR_records = PTR_records()
        self.all_records = [self.A_records, self.CNAME_records, self.PTR_records]
        
    def set_reverse(self, reverse: bool):
        self.is_reverse = reverse   
  
    def show_records(self):
        for record_type in self.all_records:
            record_type.show_records()
     
    def show_number_of_records(self):
        for record_type in self.all_records:
            record_type.show_number_of_records()        
        
    def beautify (self):
        for record_type in self.all_records:
            record_type.beautify()                
    
    def remove_duplicates(self):
        for record_type in self.all_records:
            record_type.remove_duplicates()
        
    def sort(self):
        for record_type in self.all_records:
            record_type.sort()
            
    def trim(self):
        for record_type in self.all_records:
            record_type.trim()
            
    def output_lines(self):
        lines = []
        
        for record_type in self.all_records:
            lines.extend(record_type.output_lines())
        
        return lines

   
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
        for line in file_content.copy():
            # Empty lines
            if len(line.split()) > 0:
                # Comments
                if line.strip()[0] != ";":
                    if self.find_ip_in_line(line) != None: # A, AAAA
                        if line.split()[2] == "A":
                            
                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = A_record(server_name = line_without_comment.split()[0], class_ = line_without_comment.split()[1], type_ = line_without_comment.split()[2], target = line_without_comment.split()[3])
                            
                            self.records.A_records.add_record(current_record)
                            
                        elif line.split()[2] == "AAAA":
                            pass
                    elif self.find_reverse_ip_in_line(line) != None: # PTR
                        if line.split()[2] == "PTR":
                            
                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = PTR_record(ip = line_without_comment.split()[0], class_ = line_without_comment.split()[1], type_ = line_without_comment.split()[2], domain_name = line_without_comment.split()[3])
                            self.records.PTR_records.add_record(current_record)
                        
                    elif len(line.split()) >= 4: # Other records
                        if line.split()[2] == "CNAME":
                            
                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = CNAME_record(alias = line_without_comment.split()[0], class_ = line_without_comment.split()[1], type_ = line_without_comment.split()[2], target = line_without_comment.split()[3])
                            self.records.CNAME_records.add_record(current_record)
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

    def __seperate_records_and_comments(self, line: str):
        
        record_and_comment = line.split(";")
        
        #print comment then print record
        print(f"comment : {record_and_comment}")
        
        if len(record_and_comment) == 1:
            return record_and_comment[0]
        else:
            comment = record_and_comment[1] #unused for now
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
        self.__set_list_of_DNS_records(self.file_content)
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
        
        for line in file_content.copy():
            
            # Empty lines
            if len(line.split()) > 0:
                # Comments
                if line.strip()[0] != ";":
                    if self.find_ip_in_line(line) != None: # A, AAAA
                        if line.split()[2] == "A":
                            
                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = A_record(server_name = line_without_comment.split()[0], class_ = line_without_comment.split()[1], type_ = line_without_comment.split()[2], target = line_without_comment.split()[3])                  
                            self.records.A_records.add_record(current_record)
                            file_content.remove(line)
                            
                        elif line.split()[2] == "AAAA":
                            pass
                    elif self.find_reverse_ip_in_line(line) != None: # PTR
                        if line.split()[2] == "PTR":

                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = PTR_record(ip = line_without_comment.split()[0], class_ = line_without_comment.split()[1], type_ = line_without_comment.split()[2], domain_name = line_without_comment.split()[3])
                            self.records.PTR_records.add_record(current_record)
                            file_content.remove(line)
                        
                    elif len(line.split()) >= 4: # Other records
                        print(line.split()[2])
                        if line.split()[2] == "CNAME":
                            
                            line_without_comment = self.__seperate_records_and_comments(line)
                            current_record = CNAME_record(alias = line_without_comment.split()[0], class_ = line_without_comment.split()[1], type_ = line_without_comment.split()[2], target = line_without_comment.split()[3])
                            self.records.CNAME_records.add_record(current_record)
                            file_content.remove(line)

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

    def __seperate_records_and_comments(self, line: str):
        
        record_and_comment = line.split(";")
        
        #print comment then print record
        print(f"comment : {record_and_comment}")
        
        if len(record_and_comment) == 1:
            return record_and_comment[0]
        else:
            comment = record_and_comment[1] #unused for now
            return record_and_comment[0]
            
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
        
        
        # Add the lines to the file that aren't the DNS records
        for index, line in enumerate(self.file_content):
            if  index == 2:
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
        else:
            os.rename(f"{self.name}._after_LOOM.tmp", f"{self.name}")

    def compare_to_LOOM(self, Loom_file: LOOM_file):
        
        if Loom_file.records.A_records.number_of_records() > 0:
            self.compare_A_to_LOOM(Loom_file)
        if Loom_file.records.CNAME_records.number_of_records() > 0:
            self.compare_CNAME_to_LOOM(Loom_file)
        if Loom_file.records.PTR_records.number_of_records() > 0:
            self.compare_PTR_to_LOOM(Loom_file)
    
    def compare_A_to_LOOM(self, Loom_file: LOOM_file):
        
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
                print(f"file: {self.name}\n")
                print(f"The DNS entry that translates the name server {record.server_name} to the ip address {record.target} in the LOOM file, is not present in the local DNS file {self.name}.")
                print("But, the following entry/s is/are present in the local DNS file and translate to the same ip address. \n")
                
                for line in self.records.A_records.records:
                    if line.target == record.target:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.A_records.records:
                            if line.target == record.target:
                                self.records.A_records.remove_record(line)
                        self.records.A_records.add_record(record)
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
                
                for line in self.records.A_records.records:
                    if line.server_name == record.server_name:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.A_records.records:
                            if line.server_name == record.server_name:
                                self.records.A_records.remove_record(line)
                        self.records.A_records.add_record(record)
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
                        self.records.A_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
                    else:
                        print(f"invalide input, please try again.")    

        print("\n", "-" * 80, "\n")             
        # Show the the records of the DNS file
        self.records.show_records()
    
    def compare_CNAME_to_LOOM(self, Loom_file: LOOM_file):
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
                print(f"file: {self.name}\n")
                print(f"The DNS entry that makes the alias {record.alias} point to the target {record.target} in the LOOM file, is not present in the local DNS file {self.name}.")
                print(f"But, the following entry/s is/are present in the local DNS resovles the same alias.\n")
                
                for line in self.records.CNAME_records.records:
                    if line.alias == record.alias:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.CNAME_records.records:
                            if line.alias == record.alias:
                                self.records.CNAME_records.remove_record(line)
                        self.records.CNAME_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
                    else:
                        print(f"invalide input, please try again.")
                        
            elif record not in records_same_alias:
                print(f"file: {self.name}\n")
                print(f"The DNS entry that makes the alias {record.alias} point to the target {record.target} in the LOOM file, is not present in the local DNS file {self.name}.")
                print(f"See the entry below. \n")
                record.show()
                
                for attempt in range(3):
                    answer = input(f"Would you like to add that entry to the local DNS file {self.name} ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"Adding the entry to the local DNS file {self.name} ...")
                        self.records.CNAME_records.add_record(record)
                        break
                    elif answer.lower() == "n" or answer == "":
                        logger.info(f"The entry will not be added to the local DNS file {self.name}.")
                        break
                    else:
                        print(f"invalide input, please try again.")
        
               
    def compare_PTR_to_LOOM(self, Loom_file: LOOM_file):
        
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
                print(f"file: {self.name}\n")
                print(f"The DNS entry that translates the ip address {record.ip} to the domain name {record.domain_name} in the LOOM file, is not present in the local DNS file {self.name}.")
                print("But, the following entry/s is/are present in the local DNS file and translate the same ip address\n")
                
                for line in self.records.PTR_records.records:
                    if line.ip == record.ip:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.PTR_records.records:
                            if line.ip == record.ip:
                                self.records.PTR_records.remove_record(line)
                        self.records.PTR_records.add_record(record)
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
                
                for line in self.records.PTR_records.records:
                    if line.domain_name == record.domain_name:
                        line.show()
                        
                for attempt in range(3):
                    answer = input(f"Would you like to replace that entry in the local DNS file with the entry in the LOOM file ? (y/N) : ")
                    if answer.lower() == "y":
                        logger.info(f"replacing the entry in local DNS file {self.name} ...")
                        for line in self.records.PTR_records.records:
                            if line.domain_name == record.domain_name:
                                self.records.PTR_records.remove_record(line)
                        self.records.PTR_records.add_record(record)
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
                        self.records.PTR_records.add_record(record)
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

if __name__ == "__main__":
                
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
        file.beautify_DNS_entries()
        logger.info(f"sorting the DNS entries for {file.name} ...")
        file.sort_DNS_entries()
        logger.info(f"reconstructing the file {file.name} ...")
        file.reconstruct_file()
        logger.info(f"replacing the old file with the new one for {file.name} ...")
        file.replace_file()


    logger.info("The program has finished running.")
