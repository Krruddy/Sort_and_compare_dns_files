import argparse


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="A DNS sorter.")
        self.parser.add_argument(
            "-f", "--files",
            nargs='+',
            type=str,
            help="List of the DNS files that will be treated by the program"
        )
        self.parser.add_argument(
            "-l", "--loom",
            type=str,
            help="Path to the loom directory"
        )

    def parse_arguments(self):
        return self.parser.parse_args()
