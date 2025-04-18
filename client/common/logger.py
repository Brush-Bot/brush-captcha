import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")

    # 控制台输出
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 文件输出（按模块名称区分）
    fh = RotatingFileHandler(f"{LOG_DIR}/{name}.log", maxBytes=10 * 1024 * 1024, backupCount=3)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
# common/emoji_log.py
def emoji(level: str, message: str) -> str:
    tags = {
        "DEBUG": "🐞",
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
        "TASK": "📌",
        "GETTASK":"📥",
        "STARTUP": "🚀",
        "SHUTDOWN": "🛑",
        "NETWORK": "🌐",
        "DB": "🗃️",
        "WAIT":"⏳",
    }
    return f"{tags.get(level.upper(), '')} {message}"