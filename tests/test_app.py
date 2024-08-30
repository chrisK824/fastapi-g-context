from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from fastapi_g_context import GlobalsMiddleware, g
import asyncio


app = FastAPI()
app.add_middleware(GlobalsMiddleware)


async def set_globals():
    g.username = "JohnDoe"
    g.request_id = "123456"
    g.is_admin = True
    g.to_pop = "dispensable"


@app.get("/set_globals", dependencies=[Depends(set_globals)])
async def set_globals_endpoint():
    return {
        "global_keys": list(g.keys()),
        "global_values": list(g.values()),
        "global_dict": g.to_dict(),
    }


@app.get("/no_globals")
async def no_globals_endpoint():
    return {
        "global_keys": list(g.keys()),
        "global_values": list(g.values()),
        "global_dict": g.to_dict(),
    }

client = TestClient(app)


def test_globals_are_set():
    response = client.get("/set_globals")
    assert response.status_code == 200
    data = response.json()
    assert set(data["global_keys"]) == {"username", "request_id", "is_admin", "to_pop"}
    assert data["global_dict"]["username"] == "JohnDoe"
    assert data["global_dict"]["request_id"] == "123456"
    assert data["global_dict"]["is_admin"] is True


def test_globals_isolation_across_different_endpoints():
    response = client.get("/set_globals")
    assert response.status_code == 200
    data = response.json()
    assert set(data["global_keys"]) == {"username", "request_id", "is_admin", "to_pop"}
    assert data["global_dict"]["username"] == "JohnDoe"
    assert data["global_dict"]["request_id"] == "123456"
    assert data["global_dict"]["is_admin"] is True

    response = client.get("/no_globals")
    assert response.status_code == 200
    data = response.json()

    assert data["global_dict"] == {}
    assert data["global_keys"] == []
    assert data["global_values"] == []


def test_globals_isolation_across_different_endpoints_async():
    async def request_set_globals():
        response = client.get("/set_globals")
        return response.json()

    async def request_no_globals():
        response = client.get("/no_globals")
        return response.json()

    async def main():
        response1, response2 = await asyncio.gather(
            request_set_globals(),
            request_no_globals()
        )

        assert response1["global_dict"]["username"] == "JohnDoe"
        assert response1["global_dict"]["request_id"] == "123456"
        assert response1["global_dict"]["is_admin"] is True

        assert response2["global_dict"] == {}

    asyncio.run(main())


def test_concurrent_requests():
    async def request_set_globals():
        response = client.get("/set_globals")
        return response.json()

    async def request_no_globals():
        response = client.get("/no_globals")
        return response.json()

    async def main():
        response1, response2, response3, response4 = await asyncio.gather(
            request_set_globals(),
            request_set_globals(),
            request_no_globals(),
            request_no_globals()
        )

        for response in [response1, response2]:
            assert response["global_dict"]["username"] == "JohnDoe"
            assert response["global_dict"]["request_id"] == "123456"
            assert response["global_dict"]["is_admin"] is True

        for response in [response3, response4]:
            assert response["global_dict"] == {}

    asyncio.run(main())
