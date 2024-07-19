import uvicorn

def run():
    uvicorn.run("api.api:app",host="0.0.0.0", reload = False)

if __name__ == "__main__":
    print("starting server")
    run()