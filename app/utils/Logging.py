import logging
from logging.handlers import RotatingFileHandler
import os

class Logging():
    def __init__(self, name:str = "appointment_app"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)

            file_handler =RotatingFileHandler(  
                f"{log_dir}/app.log",
                maxBytes=2 * 1024 * 1024,
                backupCount= 3,
                encoding="utf-8",
                delay=True
                )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            error_handler = logging.FileHandler(f"{log_dir}/error.log")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(error_handler)

    def get_logger(self):
        return self.logger