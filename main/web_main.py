import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from main.log_analyzer import LogAnalyzerFactory
from main.connector import SshConnector
from region import REGION_DICT
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

# noinspection PyTypeChecker
ssh_connector_dict: dict = {}
db_info_dict : dict = {}

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


@app.websocket('/ws/ffprobe/{region_id}')
async def ffprobe(ws: WebSocket, region_id: str):
    ssh_connector = get_ssh_connector(region_id)
    await ws.accept()
    rtsp_url = await ws.receive_text()
    print(f'rtsp_url: {rtsp_url}')
    try:
        async for output in ssh_connector.run_ffprobe(rtsp_url):
            await ws.send_text(output)
    except WebSocketDisconnect:
        # 이게 아예 안잡히네? 왜지?
        print("socket closed")
        return

@app.websocket('/ws/realtime-view')
async def realtime_view(ws: WebSocket, region_id: str):
    ssh_connector = get_ssh_connector(region_id)
    await ws.accept()
    try:
        async for output in ssh_connector.run_realtime_view():
            print("")
    except WebSocketDisconnect:
        print("socket closed")
        return

def get_ssh_connector(region_id: str) -> SshConnector:
    global ssh_connector_dict
    if region_id in ssh_connector_dict:
        return ssh_connector_dict[region_id]

    ssh_connector = SshConnector(REGION_DICT[region_id])
    ssh_connector_dict[region_id] = ssh_connector
    return ssh_connector

def get_db_info(region_id: str):
    global db_info_dict
    if region_id in db_info_dict.keys():
        return db_info_dict[region_id]

    info = get_ssh_connector(region_id).get_db_info()
    db_info_dict[region_id] = info
    return info

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)