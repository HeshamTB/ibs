#/bin/python

import uvicorn
from typing import Optional
from fastapi import FastAPI

from pydantic import BaseModel


app = FastAPI()

class EchoType(BaseModel):
    val: str

@app.post("/echo")
def get_echo(echo: EchoType):
    return echo

if __name__ == '__main__':
    #uvicorn server:app --port 8000 --ssl-certfile server.crt --ssl-keyfile server.key
    uvicorn.run(
        'echo_server:app', port=8000, host='localhost',
        reload=False,
        ssl_keyfile='server.key',
        ssl_certfile='server.crt')
