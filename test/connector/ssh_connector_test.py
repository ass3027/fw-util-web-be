import unittest

import pexpect

from main.connector import SshConnector
from main import REGION_DICT


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        region = REGION_DICT['daegu']
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
        self.assertIsInstance(result, list)


    def test_run_loop(self):
        # region = REGION_DICT['custom']
        # url = "rtsp://user1:Wkit3031@192.168.30.15:554/profile2/media.smp"
        region = REGION_DICT['gyeongnam']
        url = 'rtsp://192.168.10.201:8554/7eecea0b-6e76-4964-9fbd-4fe79d388134'
        # region = REGION_DICT['gangwon']
        # url = "rtsp://aisanbul:1q2w3e4r5t%21@33.0.10.115:1554/video109?profile=high"
        # region = REGION_DICT['daegu']
        # url = "rtsp://admin:admin@192.168.12.252/1/stream1"
        docker_exec_cmd = "sudo -S docker exec $(sudo -S docker ps -q --filter ancestor=firewatcher:v2.1) "
        ffprobe_cmd = f"ffprobe {url}"

        sc = SshConnector(region)
        child = sc.ssh_connect()

        main_cmd = docker_exec_cmd + ffprobe_cmd
        child.sendline(main_cmd)
        sc.send_passwd_if_sudo(child, main_cmd)

        result = []
        while True:
            result = child.expect([pexpect.TIMEOUT,f'{sc.user}@'], timeout=3)
            output = child.before.decode()
            print(output)
            result.append(output)

            if result == 1:
                break

        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()
