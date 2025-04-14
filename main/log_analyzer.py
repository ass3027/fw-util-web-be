
class LogAnalyzer:
    def __init__(self, db_info_dict, log_file_path_list):
        self.db_info_dict = db_info_dict
        self.log_file_path_list = log_file_path_list
        self.time_url_dict = {}
        self.cctv_id_time_dict = {}

    # noinspection PyMethodMayBeStatic
    def get_line_by_chunk(self, log_file_path, chunk_size=100):
        with open(log_file_path, "r", encoding="utf-8") as f:
            while True:
                chunk = f.read(chunk_size)
                if chunk:
                    break

                for line in chunk:
                    yield line


    def get_connection_fail_list(self):
        for log_file_path in self.log_file_path_list:
            with log_file_path:
                self.parse_connection_fail_list(log_file_path)

        self.print()


    def parse_connection_fail_list(self, log_file_path):
        for line in self.get_line_by_chunk(log_file_path):
            if line[60] != "C" or line[60:79] != "Connect failed list":
                continue

            failed_conn_list_str = line[line.index("[") + 1: line.index("]")]
            # remove first ' and end '
            failed_conn_list = [rtsp.strip()[1:-1] for rtsp in failed_conn_list_str.split(",")]

            hour_mm = line[11:16]
            # if not hour_mm in self.dict:
            if hour_mm not in self.time_url_dict:
                self.time_url_dict[hour_mm] = failed_conn_list
            else:
                self.time_url_dict[hour_mm] += failed_conn_list


    def get_video_log_list(self, cctv_name):
        info = {}
        for db_info in self.db_info_dict.values():
            if db_info["cctv_name"] == cctv_name:
                info = db_info
                break

        log_index = info['inference_id'][4]
        with self.log_file_path_list[log_index] as log_file:
            self.parse_video_log_list(log_file ,cctv_name)


    def parse_video_log_list(self, log_file_path, cctv_name):
        pass

    def init_url_time_dict(self):
        for hour_mm in self.time_url_dict:
            for url in self.time_url_dict[hour_mm]:
                info = self.get_cctv_info_from_url(url)
                if info is None:
                    continue

                cctv_id = info["cctv_ID"]

                if not cctv_id in self.cctv_id_time_dict:
                    self.cctv_id_time_dict[cctv_id] = []

                self.cctv_id_time_dict[cctv_id].append(hour_mm)


    def get_cctv_info_from_url(self, url):
        last_path = url.split("/")[-1]
        is_media_mtx = last_path.startswith("cctv")
        if is_media_mtx:
            cctv_id = last_path.replace("cctv", "")
            return self.db_info_dict[int(cctv_id)]

        for info in self.db_info_dict.values():
            if info['url'] == url:
                return info


    def print(self):
        self.init_url_time_dict()

        for cctv_id in sorted(self.db_info_dict.keys()):
            info = self.db_info_dict[cctv_id]
            if cctv_id in self.cctv_id_time_dict:
                connection_fail_list = self.cctv_id_time_dict[cctv_id]
            else:
                connection_fail_list = []
            print(f"{cctv_id} {info['cctv_name']}: {connection_fail_list}")


if __name__ == "__main__":
    from ssh_connector import SshConnector
    from region import REGION_DICT

    _region_name = "gangwon"
    # _region_name = "gyeongnam"
    # _region_name = "jeonnam"
    # _region_name = "choongbook"
    _date = "2025-03-09"

    _region = REGION_DICT[_region_name]
    _db_info_dict = SshConnector(_region).get_db_info()
    _log_file_path_list = []
    LogAnalyzer(_db_info_dict, _log_file_path_list).get_connection_fail_list()
