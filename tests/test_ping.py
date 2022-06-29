from influxlib import Client


async def test_ping(client: Client):
    resp = await client.ping()
    assert resp.status == 204
