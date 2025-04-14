import json
import os.path
import unittest
from main.log_analyzer import LogAnalyzer
from main import REGION_DICT


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_info_dict = json.load(open('./test_data/test_db_info.json', 'r'))
        cls.region = REGION_DICT['gyeongnam']
        cls.date = "2025-03-13"
        cls.dir_path = os.path.join(os.path.dirname(__file__),"./test_data/logs/")
        cls.log_analyzer = LogAnalyzer(db_info_dict, )

    # 결과가 ScpConnector.run 에 의존
    # 심지어 지금은 그냥 os.path 에 의존임
    def test_load_log_file(self):
        result = self.log_analyzer.load_log_file(0)
        self.assertFalse(result)


    # def test_main(self):
    #     from new.log_analyzer.main import SshConnector
    #     db_info = SshConnector(REGION_DICT['gyeongnam']).get_db_info()
    #     with open("./test_data/test_db_info.json","w") as f:
    #         json.dump(db_info,f)


if __name__ == '__main__':
    unittest.main()
