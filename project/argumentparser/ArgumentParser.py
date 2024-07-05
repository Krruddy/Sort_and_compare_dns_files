import argparse


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="A DNS operation.")
        self.parser.add_argument(
            "-f", "--files",
            nargs='+',
            type=str,
            help="List of the DNS files that will be treated by the program"
        )

    def parse_arguments(self):
        return self.parser.parse_args()
