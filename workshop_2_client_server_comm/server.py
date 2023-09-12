#!/usr/bin/env python3

from fastapi import FastAPI
from pydantic import BaseModel
from time import time
import uvicorn
import os
import signal


app = FastAPI()

# This is an example of a simple server that takes in a dictionary and adds a timestamp to it.
# The server is terminated by sending a DELETE request to /terminate

class InputDict(BaseModel):
    name: str
    timestamp: str = None

@app.post("/")
def modify_dict(input_dict: InputDict):
    # Adding some rows to the dictionary
    input_dict.timestamp= str(time())
    return {
        "name": input_dict.name,
        "timestamp": input_dict.timestamp
    }

@app.delete("/terminate")
def terminate():
    os.kill(os.getpid(), signal.SIGINT)
    return "Terminated"

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)