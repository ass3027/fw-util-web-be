import os
from datetime import datetime
import pytz
from scp_connector import ScpConnector


class LogFileImporter:
    def __init__(self, region, date=None, log_file_dir=None):
        self.region = region

        self.date = date
        self.is_today = False
        if self.date is None:
            self.is_today = True
            timezone = pytz.timezone("Asia/Seoul")
            self.date = datetime.now(timezone).strftime("%Y-%m-%d")

        self.log_file_dir = log_file_dir if log_file_dir is not None \
            else os.path.join(os.path.dirname(__file__), f"log_files/{region.id}")

        os.makedirs(self.log_file_dir, exist_ok=True)

        self.log_file_path_list = [
            os.path.join(self.log_file_dir, f"{region.id}-{self.date}_{i}.log")
            for i in [0, 1]
        ]


    def load_log_file(self, index):
        source = f"/home/workspace/logs/controller/{self.date}_{index}.log"
        print(f"Loading {source}...")

        log_file_path = self.log_file_path_list[index]
        if not self.is_today and os.path.exists(log_file_path):
            print(f"log file is already loaded: {log_file_path}")
        else:
            sc = ScpConnector(self.region)
            sc.run(source, log_file_path)

        return open(log_file_path, "r", encoding="utf-8")