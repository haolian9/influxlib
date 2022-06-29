import trio

from influxlib import Client, Context


async def main():
    ctx = Context("http://127.0.0.1:8086", "token", "org", "bucket")
    async with Client.from_context(ctx) as client:
        resp = await client.ping()
        assert resp.status == 204


if __name__ == "__main__":
    trio.run(main)
