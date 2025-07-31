import unittest
import time

from main.forest_api import ForestAPI, FireInfoDTO


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forest_api = ForestAPI()

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_default(self):
        fire_info_dto = FireInfoDTO(
            '20250601', '20250714', '서울특별시'
        )
        result = self.forest_api.get_fire_info(fire_info_dto)
        print(result)

    def test_all_region(self):
        fire_info_dto = FireInfoDTO(
            '20250601', '20250714',
        )
        result = self.forest_api.get_fire_info(fire_info_dto)
        print(result)

    def test_api_limitation(self):
        fire_info_dto = FireInfoDTO(
            '20250601', '20250714',
        )

        for i in range(60):
            result = self.forest_api.get_fire_info(fire_info_dto)
            print(result)
            time.sleep(60)

if __name__ == '__main__':
    unittest.main()
