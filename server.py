import uvicorn

def run():
    uvicorn.run("api.api:app",host="0.0.0.0", reload = True)

if __name__ == "__main__":
    run()