import logging
import os
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LoggerConfig:
    def __init__(self):
        self.log_level = os.environ.get("LOG_LEVEL", LogLevel.INFO.value)
        self.log_frequency = float(os.environ.get("LOG_FREQUENCY", "5.0"))
        self.log_format = os.environ.get(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.console_format = os.environ.get(
            "CONSOLE_FORMAT",
            "[%(asctime)s] %(levelname)s - %(message)s"
        )
        self.log_file_path = os.environ.get("LOG_FILE_PATH", "/app/logs/app.log")
        self.max_file_size_mb = float(os.environ.get("MAX_FILE_SIZE_MB", "1"))
        self.web_port = int(os.environ.get("WEB_PORT", "8080"))

    def get_logging_level(self):
        level_mapping = {
            LogLevel.DEBUG.value: logging.DEBUG,
            LogLevel.INFO.value: logging.INFO,
            LogLevel.WARNING.value: logging.WARNING,
            LogLevel.ERROR.value: logging.ERROR,
            LogLevel.CRITICAL.value: logging.CRITICAL
        }
        return level_mapping.get(self.log_level, logging.INFO)

    def to_dict(self):
        return {
            "log_level": self.log_level,
            "log_frequency": self.log_frequency,
            "log_format": self.log_format,
            "console_format": self.console_format,
            "log_file_path": self.log_file_path,
            "max_file_size_mb": self.max_file_size_mb,
            "web_port": self.web_port
        }