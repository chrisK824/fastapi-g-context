from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from fastapi_g_context import GlobalsMiddleware, g
import asyncio
import pytest
import functools


if not hasattr(asyncio, 'to_thread'):
    async def to_thread(func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
else:
    to_thread = asyncio.to_thread


app = FastAPI()
app.add_middleware(GlobalsMiddleware)


async def initialize_global_context():
    g.username = "JohnDoe"
    g.request_id = "123456"
    g.is_admin = True
    g.to_remove = "dispensable"


@app.get("/set_globals", dependencies=[Depends(initialize_global_context)])
async def set_globals_view():
    return {
        "global_keys": list(g.keys()),
        "global_values": list(g.values()),
        "global_data": g.to_dict(),
    }


@app.get("/no_globals")
async def no_globals_view():
    return {
        "global_keys": list(g.keys()),
        "global_values": list(g.values()),
        "global_data": g.to_dict(),
    }


@app.get("/set_globals_with_delay", dependencies=[Depends(initialize_global_context)])
async def set_globals_with_delay_view():
    await asyncio.sleep(2)
    return {
        "global_keys": list(g.keys()),
        "global_values": list(g.values()),
        "global_data": g.to_dict(),
    }


@app.get("/no_globals_with_delay")
async def no_globals_with_delay_view():
    await asyncio.sleep(5)
    return {
        "global_keys": list(g.keys()),
        "global_values": list(g.values()),
        "global_data": g.to_dict(),
    }


client = TestClient(app)


def test_set_globals():
    response = client.get("/set_globals")
    assert response.status_code == 200
    data = response.json()
    assert set(data["global_keys"]) == {"username", "request_id", "is_admin", "to_remove"}
    assert data["global_data"]["username"] == "JohnDoe"
    assert data["global_data"]["request_id"] == "123456"
    assert data["global_data"]["is_admin"] is True


def test_globals_isolation_between_endpoints():
    response = client.get("/set_globals")
    assert response.status_code == 200
    data = response.json()
    assert set(data["global_keys"]) == {"username", "request_id", "is_admin", "to_remove"}
    assert data["global_data"]["username"] == "JohnDoe"
    assert data["global_data"]["request_id"] == "123456"
    assert data["global_data"]["is_admin"] is True

    response = client.get("/no_globals")
    assert response.status_code == 200
    data = response.json()
    assert data["global_data"] == {}
    assert data["global_keys"] == []
    assert data["global_values"] == []


def test_async_globals_isolation():
    async def make_request_to_set_globals():
        response = client.get("/set_globals")
        return response.json()

    async def make_request_to_no_globals():
        response = client.get("/no_globals")
        return response.json()

    async def test_globals_isolation_async():
        response1, response2 = await asyncio.gather(
            make_request_to_set_globals(),
            make_request_to_no_globals()
        )

        assert response1["global_data"]["username"] == "JohnDoe"
        assert response1["global_data"]["request_id"] == "123456"
        assert response1["global_data"]["is_admin"] is True

        assert response2["global_data"] == {}

    asyncio.run(test_globals_isolation_async())


def test_concurrent_global_requests():
    async def make_request_to_set_globals():
        response = client.get("/set_globals")
        return response.json()

    async def make_request_to_no_globals():
        response = client.get("/no_globals")
        return response.json()

    async def test_concurrent_requests_async():
        response1, response2, response3, response4 = await asyncio.gather(
            make_request_to_set_globals(),
            make_request_to_set_globals(),
            make_request_to_no_globals(),
            make_request_to_no_globals()
        )

        for response in [response1, response2]:
            assert response["global_data"]["username"] == "JohnDoe"
            assert response["global_data"]["request_id"] == "123456"
            assert response["global_data"]["is_admin"] is True

        for response in [response3, response4]:
            assert response["global_data"] == {}

    asyncio.run(test_concurrent_requests_async())


@pytest.mark.asyncio
async def test_concurrent_requests_with_sleep_delay():

    def make_request_set_globals_with_delay():
        response = client.get("/set_globals_with_delay")
        return response.json()

    def make_request_no_globals_with_delay():
        response = client.get("/no_globals_with_delay")
        return response.json()

    task_1 = asyncio.create_task(to_thread(make_request_set_globals_with_delay))

    await asyncio.sleep(1)
    task_2 = asyncio.create_task(to_thread(make_request_no_globals_with_delay))

    response_1 = await task_1
    response_2 = await task_2

    assert "username" in response_1["global_keys"]
    assert response_1["global_data"]["username"] == "JohnDoe"
    assert response_1["global_data"]["request_id"] == "123456"
    assert response_1["global_data"]["is_admin"] is True

    assert response_2["global_keys"] == []
    assert response_2["global_data"] == {}
