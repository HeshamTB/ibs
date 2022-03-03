#/bin/python

import uvicorn
from typing import Optional
from fastapi import FastAPI

from pydantic import BaseModel

class UserAuthForEntity(BaseModel):
    username: str
    passwd: str
    entitiy: int

app = FastAPI()

@app.post("/isauth")
def is_auth(user_auth_for_entity: UserAuthForEntity):
    return user_auth_for_entity

if __name__ == '__main__':
    #uvicorn server:app --port 8000 --ssl-certfile server.crt --ssl-keyfile server.key
    uvicorn.run(
        'server:app', port=4433, host='0.0.0.0',
        reload=False,
        ssl_keyfile='server.key',
        ssl_certfile='server.crt')
