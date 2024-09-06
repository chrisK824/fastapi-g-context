from __future__ import absolute_import
import uvicorn
from fastapi import FastAPI, Depends
import asyncio
# from fastapi_g_context.fastapi_g import g, GlobalsMiddleware
from fastapi_g_context import g, GlobalsMiddleware
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
app.add_middleware(GlobalsMiddleware)


async def set_globals():
    g.username = "JohnDoe"


@app.get("/set_globals1", dependencies=[Depends(set_globals)])
async def set_globals_endpoint_1():
    print(g.username)
    await asyncio.sleep(2)
    print(g.username)


@app.get("/set_globals2")
async def set_globals_endpoint_2():
    await asyncio.sleep(5)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)