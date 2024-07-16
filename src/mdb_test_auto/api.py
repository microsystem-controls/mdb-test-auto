import time
from fastapi import FastAPI

from mdb import MDB
from .utils import create_device_info
from .schema import DeviceInfo

app = FastAPI()
mdb = MDB()



@app.get("/api/dispense")
def dispense(coin_type:int):
    return mdb.dispense(coin_type, 1)

@app.get("/api/device_info")
def get_device_info() -> DeviceInfo:
    data = mdb.id()
    return create_device_info(data[0], data[1])

@app.get("/api/poll")
def poll():
    return mdb.poll()

