import os
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template
from config import LoggerConfig

class RotatingLogger:
    def __init__(self, config):
        self.config = config
        self.log_file_path = Path(config.log_file_path)
        self.max_size_bytes = config.max_file_size_mb * 1024 * 1024
        self.recent_logs = []
        self.max_recent_logs = 100

        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger("DistributedLogger")
        self.logger.setLevel(self.config.get_logging_level())

        self.logger.handlers.clear()

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(self.config.console_format)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        file_handler = logging.FileHandler(self.log_file_path)
        file_formatter = logging.Formatter(self.config.log_format)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def check_rotation(self):
        if self.log_file_path.exists() and self.log_file_path.stat().st_size > self.max_size_bytes:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_name = self.log_file_path.with_suffix(f".{timestamp}.log")
            self.log_file_path.rename(rotated_name)

            self.setup_logging()
            self.logger.info(f"Log file rotated to {rotated_name}")

    def log(self, level, message):
        self.check_rotation()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }

        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > self.max_recent_logs:
            self.recent_logs.pop(0)

        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "CRITICAL":
            self.logger.critical(message)

def create_web_app(rotating_logger, config):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template(
            'dashboard.html',
            config=config.to_dict(),
            logs=rotating_logger.recent_logs[-20:],
            log_count=len(rotating_logger.recent_logs)
        )

    @app.route('/api/logs')
    def api_logs():
        return jsonify(rotating_logger.recent_logs[-50:])

    @app.route('/api/config')
    def api_config():
        return jsonify(config.to_dict())

    return app

def logger_service(rotating_logger, config):
    rotating_logger.log("INFO", "Starting distributed logger service...")
    rotating_logger.log("INFO", f"Log level set to: {config.log_level}")
    rotating_logger.log("INFO", f"Log frequency: {config.log_frequency} seconds")
    rotating_logger.log("INFO", f"Max file size: {config.max_file_size_mb}MB")

    counter = 0
    while True:
        counter += 1

        if counter % 10 == 0:
            rotating_logger.log("WARNING", f"Warning message example #{counter//10}")
        elif counter % 20 == 0:
            rotating_logger.log("ERROR", f"Error message example #{counter//20}")
        else:
            rotating_logger.log("INFO", f"Logger service is running #{counter}. This is part of our distributed system!")

        time.sleep(config.log_frequency)

def main():
    config = LoggerConfig()
    rotating_logger = RotatingLogger(config)

    app = create_web_app(rotating_logger, config)

    logger_thread = threading.Thread(target=logger_service, args=(rotating_logger, config))
    logger_thread.daemon = True
    logger_thread.start()

    rotating_logger.log("INFO", f"Starting web interface on port {config.web_port}")
    app.run(host='0.0.0.0', port=config.web_port, debug=False)

if __name__ == "__main__":
    main()