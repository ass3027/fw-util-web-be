import requests


class FireInfoDTO:
    def __init__(self, start_dt, end_dt, region_name=''):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.region_name = region_name

class ForestAPI:
    def __init__(self):
        self.region_code_dict = {
            '': '',
            '서울특별시': '11',
            '부산광역시': '26',
            '대구광역시': '27',
            '인천광역시': '28',
            '광주광역시': '29',
            '대전광역시': '30',
            '울산광역시': '31',
            '세종특별자치시': '36',
            '경기도': '41',
            '충청북도': '43',
            '충청남도': '44',
            '전라남도': '46',
            '경상북도': '47',
            '경상남도': '48',
            '제주특별자치도': '50',
            '강원특별자치도': '51',
            '전북특별자치도': '52'
        }

    def get_fire_info(self, dto: FireInfoDTO):
        url = "https://fd.forest.go.kr/ffas/pubConn/occur/getPublicShowFireInfoList.do"
        payload = {
            'pager': {
                'pageListStart': 0,
                'pageListEnd': 10,
                'perPage': '30',
                'perPageList': 10
            },
            'param': {
                'startDtm': dto.start_dt,
                'endDtm': dto.end_dt,
                'regionCode': self.region_code_dict[dto.region_name],
                'issueCode': '',
            }
        }
        res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        # print(res)
        # print(res.reason)
        # print(res.content)
        # print(res.request.body)
        print(res.json())
        return res.json()


