import pytest

from influxlib import Client, Context


@pytest.fixture
async def client():
    c = Client.from_context(
        Context(
            "http://127.0.0.1:8086",
            "CJWibQXgp7vx2FXk0H6ahv07ZSvEjWsdBInP6V-LhGOFJgR_VaJSaGPxo2jTvfT7DH7W9MjeN6muKKpC5dLCpg==",
            "org",
            "bucket",
        )
    )

    async with c:
        yield c
