import unittest
from main.ssh_connector import SshConnector
from main.region import REGION_DICT


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        region = REGION_DICT['custom']
        cls.ssh_connector = SshConnector(region)

    def test_init(self):
        self.assertIsNotNone(self.ssh_connector)


    def test_connect(self):
        main_cmd = "sudo echo connect-test"

        result = self.ssh_connector.run(main_cmd)
        result = result.replace("\r\n", "")
        self.assertEqual("connect-test", result)

    def test_get_db_info(self):
        result = self.ssh_connector.get_db_info()
        self.assertEqual(0, len(result))


    def test_run_ffprobe(self):
        url = "rtsp://user1:Wkit3031@192.168.30.15:554/profile2/media.smp"
        result = self.ssh_connector.run_ffprobe(url)
        # print(result)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
