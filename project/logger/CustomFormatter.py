import logging


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
