from fastapi import FastAPI
from threading import Thread
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bot activo con FastAPI!"}

def run():
    uvicorn.run(app, host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
