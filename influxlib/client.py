import logging

import attrs
from httpcore import URL, AsyncConnectionPool, Request, Response


@attrs.define
class Context:
    url: str
    token: str
    org: str
    bucket: str
    precision: str = attrs.field(default="ns")


@attrs.define
class Client:
    _base_url: URL
    _pool: AsyncConnectionPool
    _mandatory_headers: list[tuple[bytes, bytes]]
    _write_target: bytes

    @classmethod
    def from_context(cls, ctx: Context) -> "Client":
        base_url = URL(ctx.url)
        assert base_url.target == b"/"

        if base_url.port:
            host = "{!s}:{}".format(base_url.host.decode(), base_url.port).encode()
        else:
            host = base_url.host

        headers = [
            (b"Host", host),
            (b"Accept", b"application/json"),
            (b"Content-Type", b"text/plain; charset=utf-8"),
            (
                b"Authorization",
                "Token {}".format(ctx.token).encode(),
            ),
        ]

        write_params = "{}?org={}&bucket={}&precision={}".format(
            "/api/v2/write", ctx.org, ctx.bucket, ctx.precision
        ).encode()

        pool = AsyncConnectionPool()

        return cls(base_url, pool, headers, write_params)

    async def __aenter__(self):
        await self._pool.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._pool.__aexit__()

    def _build_url(self, target: bytes) -> URL:
        assert target.startswith(b"/")
        return URL(
            scheme=self._base_url.scheme,
            host=self._base_url.host,
            port=self._base_url.port,
            target=target,
        )

    def _build_request(self, method: bytes, target: bytes, data: bytes = b""):
        req = Request(method, self._build_url(target), headers=None, content=data)
        if data == b"":
            req.headers = self._mandatory_headers
        else:
            req.headers.extend(self._mandatory_headers)
            req.headers.append((b"Content-Length", str(len(data)).encode()))
        logging.debug("request: %s %s headers=%s", req.method, req.url, req.headers)
        return req

    async def _roundtrip(self, req: Request):
        resp = await self._pool.handle_async_request(req)
        await resp.aread()
        await resp.aclose()
        return resp

    async def ping(self) -> Response:
        req = self._build_request(b"GET", b"/ping")
        return await self._roundtrip(req)

    async def write(self, line: bytes) -> Response:
        req = self._build_request(b"POST", self._write_target, line)
        return await self._roundtrip(req)

    async def write_many(self, *lines: bytes) -> Response:
        req = self._build_request(b"POST", self._write_target, b"\n".join(lines))
        return await self._roundtrip(req)
