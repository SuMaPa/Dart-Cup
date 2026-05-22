import logging
import os

os.makedirs("logs", exist_ok=True)

def setup_logger():
    logger = logging.getLogger("DartGameLogger")
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler("logs/error.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()
