import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from main.log_analyzer import LogAnalyzerFactory
from main.connector import SshConnector
from region import Region, REGION_DICT
app = FastAPI()
origins = [ "http://localhost","http://localhost:5173" ]
origin_regex = "http://192.168.*"

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_region : Region = REGION_DICT['custom']
_ssh_connector :SshConnector = SshConnector(current_region)
db_info_dict : dict = {}

def on_change_region(_region):
    global current_region, db_info_dict, _ssh_connector
    current_region = _region
    _ssh_connector = SshConnector(current_region)
    db_info_dict = _ssh_connector.get_db_info()

# on_change_region(REGION_DICT['custom'])

def get_ssh_connector(_region:str):
    global _ssh_connector
    if _ssh_connector.region.name != _region:
        _ssh_connector = SshConnector(REGION_DICT[_region])

    return _ssh_connector


@app.get("/region-dict")
def get_region_dict():
    return REGION_DICT

@app.get('/connection-fail-list')
async def connection_fail_list(region_id: str):
    log_analyzer = LogAnalyzerFactory.create(
        REGION_DICT[region_id],
        get_db_info(region_id)
    )
    return log_analyzer.get_connection_fail_list()

@app.get('/db-info')
async def db_info(region_id: str):
    return get_db_info(region_id)

# TODO 이건 ffprobe 특성상 응답이 조금씩 계속 나와서 socket 으로 해야할 듯
@app.get('/ffprobe')
async def ffprobe(rtsp_url: str):
    global _ssh_connector
    return _ssh_connector.run_ffprobe(rtsp_url)


def get_db_info(region_id: str):
    global db_info_dict
    if region_id in db_info_dict.keys():
        return db_info_dict[region_id]

    info = get_ssh_connector(region_id).get_db_info()
    db_info_dict[region_id] = info
    return info


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)