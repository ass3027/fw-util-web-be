from main.log_analyzer import ( LogFileImporter, LogAnalyzer )
from main.connector import SshConnector


class LogAnalyzerFactory:

    @staticmethod
    def create(region, db_info_dict=None, date=None, log_file_dir=None) -> LogAnalyzer:
        if db_info_dict is None:
            ssh_connector = SshConnector(region)
            db_info_dict = ssh_connector.get_db_info()

        log_file_importer = LogFileImporter(region, date, log_file_dir)
        log_file_path_list = [log_file_importer.load_log_file(i) for i in [0,1] ]

        log_analyzer = LogAnalyzer(db_info_dict, log_file_path_list)
        return log_analyzer

