from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mdb import MDB, CoinTypesToDespense
from .utils import create_device_info
from .schema import DeviceInfo

app = FastAPI()
mdb = MDB()

origins = [
    'http://127.0.0.1:8000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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

@app.get("/api/status")
def get_test_status():
    return mdb.test_status

@app.delete("/api/run")
def cancel_test():
    mdb.cancel_running_test()


@app.post("/api/run")
def run_test(cycles: dict[int,int]):
    coins_to_dispense = []
    for coin_type in cycles:
        coin_to_dispense = CoinTypesToDespense(coin_type, cycles[coin_type])
        coins_to_dispense.append(coin_to_dispense)

    mdb.run_test(coins_to_dispense)

@app.get("/api/results")
def get_test_results():
    return mdb.test_result


## user interface

app.mount("/static", StaticFiles(directory="user_interface/static"), name="static")

templates = Jinja2Templates(directory="user_interface/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

