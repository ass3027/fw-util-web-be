import json
import os.path


class Region:
    def __init__(self, id, name, user, pw, ip, port):
        self.id = id
        self.name = name
        self.user = user
        self.pw = pw
        self.ip = ip
        self.port = port

region_json_path = os.path.abspath('../region.json')
region_list = [
    Region(**region)
    for region in json.load(open(region_json_path, 'r', encoding='utf-8'))
]

REGION_DICT = {}
for region in region_list:
    REGION_DICT[region.id] = region

