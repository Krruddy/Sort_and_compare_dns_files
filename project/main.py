import re
import os
import sys
import logging
import errno
import dns.zone
import dns.rdatatype
import dns.rdataclass
import argparse
from pathlib import Path

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
from project.operation.Sorter import Sorter

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
# TODO create an abstract class for LOOMFile and DNSFile

# raised when the entries in the DNS file and the LOOM file are identical


# Create a logger
logger = logging.getLogger("my_logger")

# Create a StreamHandler and set the custom formatter
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())

# Add the handler to the logger
logger.addHandler(handler)

# Set the logging level
logger.setLevel(logging.INFO)


if __name__ == "__main__":

    # New
    ## Initialize the path to the DNS files and to the LOOM directory
    arg_parser = ArgumentParser()
    args = arg_parser.parse_arguments()
    files = [Path(file) for file in args.files]
    loom = Path(args.loom)

    sorter = Sorter(files)
    sorter.sort()


    # Old
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
                logger.warning(
                    f"The path to the LOOM directory is not specified, using the path predefined in the program.")

            # populates the list of DNS_files
            DNS_files = []
            logger.info(f"Populating the DNS list ...")
            for index, argument in enumerate(sys.argv):
                if argument == "--LOOM_path" or sys.argv[index - 1] == "--LOOM_path":
                    continue
                elif index != 0:
                    logger.info(f"adding {argument} to the list of DNS files ...")
                    #DNS_files += [DNSFile(argument)]
                    print(f"-" * 80)

            return DNS_files, LOOM_path

    logger.info("Starting the program.")

    DNS_files, LOOM_path = parse_arguments()

    if LOOM_path == None:
        LOOM_path = manual_LOOM_path

    # increments the value to increment, deletes the duplicate entries, sorts the DNS entries, reconstructs the file and replaces the old file with the new one
    for file in DNS_files:
        logger.info(f"incrementing the value for {file.path} ...")
        file.increment_incre_value()
        logger.info(f"deleting the duplicate entries for {file.path} ...")
        file.beautify()
        file.remove_duplicates()
        logger.info(f"sorting the DNS entries for {file.path} ...")
        file.sort()
        logger.info(f"reconstructing the file {file.path} ...")
        file.reconstruct_file()
        logger.info(f"replacing the old file with the new one for {file.path} ...")
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
            ##Loom_file = LOOMFile(LOOM_path, file)
            ##LOOM_files += [Loom_file]
            ##file.LOOMFile = Loom_file
            print()

        except FileNotFoundError:
            print(f"-" * 80)
            continue

    for file in DNS_files:
        print(f"-" * 80)
        print(f"Comparing the DNS file {file.path} with the LOOM file {file.LOOMFile.name} ...")
        file.compare_to_LOOM(file.LOOMFile)
        file.beautify()
        logger.info(f"sorting the DNS entries for {file.path} ...")
        file.sort()
        logger.info(f"reconstructing the file {file.path} ...")
        file.reconstruct_file()
        logger.info(f"replacing the old file with the new one for {file.path} ...")
        file.replace_file()

    logger.info("The program has finished running.")
