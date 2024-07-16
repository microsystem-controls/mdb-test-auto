import uvicorn

def run():
    uvicorn.run("mdb_test_auto.api:app",host="0.0.0.0", reload = True)

if __name__ == "__main__":
    run()