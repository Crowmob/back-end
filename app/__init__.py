import logging
import sys
import os

os.makedirs("logs", exist_ok=True)

log_level = logging.INFO
log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("logs/app.log", mode="a")

formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(log_level)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
