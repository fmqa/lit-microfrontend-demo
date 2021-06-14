from inspect import isawaitable
from pathlib import Path
from typing import Optional
from aiohttp import web
from aiohttp.signals import Signal
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound, HTTPOk
from aiohttp.web_middlewares import middleware, normalize_path_middleware
from dataclasses import asdict
import fastjsonschema
from argparse import ArgumentParser
from kickerapp import storage
from kickerapp.domain import Membership, Player, PlayerRequest, Team, Tournament

@middleware
async def schema_validation_middleware(request: web.Request, handler):
    """Catches JsonSchemaValueException and re-raises as HTTPBadRequest."""
    try:
        return await handler(request)
    except fastjsonschema.JsonSchemaValueException as e:
        raise HTTPBadRequest(reason=e.message)

def install(module, *, into: web.Application, under: Optional[str] = None):
    """Installs a module into the application and connects any defined signals."""
    for attr in dir(module):
        fn = getattr(module, attr)
        if attr.startswith("on_") and callable(fn):
            try:
                signal = getattr(into, attr)
            except AttributeError:
                pass
            else:
                if isinstance(signal, Signal):
                    signal.append(fn)
                    if under is not None:
                        into[under] = module

def profiles(routes: web.RouteTableDef, *, prefix: str = "/profiles"):
    """Profile API."""

    @routes.post(prefix)
    async def _(request: web.Request):
        storage = request.app["storage"]
        body = await request.json()
        data = storage.save(Player.create(**body), **request.app)
        data = asdict((await data) if isawaitable(data) else data)
        return web.json_response(data)

    @routes.get(prefix + "/{name}")
    async def _(request: web.Request):
        storage = request.app["storage"]
        name = request.match_info["name"]
        data = storage.load(PlayerRequest(name=name), **request.app)
        if isawaitable(data):
            data = await data
        if data is None:
            raise HTTPNotFound
        return web.json_response(asdict(data))

    @routes.delete(prefix + "/{name}")
    async def _(request: web.Request):
        storage = request.app["storage"]
        name = request.match_info["name"]
        if storage.delete(PlayerRequest(name=name), **request.app):
            raise HTTPOk
        else:
            raise HTTPNotFound
    
    @routes.get(prefix)
    async def _(request: web.Request):
        storage = request.app["storage"]
        data = storage.load(Player.Index(), **request.app)
        if isawaitable(data):
            data = await data
        return web.json_response(list(map(asdict, data)))

    return routes

def teams(routes: web.RouteTableDef, *, prefix: str = "/teams"):
    """Team API."""
    @routes.get(prefix)
    async def _(request: web.Request):
        storage = request.app["storage"]
        data = storage.load(Team.Index(), **request.app)
        if isawaitable(data):
            data = await data
        return web.json_response(list(map(asdict, data))) 

    @routes.post(prefix)
    async def _(request: web.Request):
        storage = request.app["storage"]
        body = await request.json()
        data = storage.save(Team.create(**body), **request.app)
        if isawaitable(data):
            data = await data
        if data is None:
            raise HTTPOk
        else:
            return web.json_response(asdict(data))
    
    @routes.delete(prefix + "/{name}")
    async def _(request: web.Request):
        storage = request.app["storage"]
        name = request.match_info["name"]
        if storage.delete(Team(name=name), **request.app):
            raise HTTPOk
        else:
            raise HTTPNotFound

    return routes

def memberships(routes: web.RouteTableDef, *, prefix: str = "/memberships"):
    """Team membership API."""
    @routes.post(prefix)
    async def _(request: web.Request):
        storage = request.app["storage"]
        body = await request.json()
        try:
            data = storage.save(Membership.create(**body), **request.app)
            if isawaitable(data):
                data = await data
        except ValueError:
            raise HTTPBadRequest(reason="Unknown player or team name")
        if data is None:
            raise HTTPOk
        else:
            return web.json_response(asdict(data))
    return routes

def tournaments(routes: web.RouteTableDef, *, prefix: str = "/tournaments"):
    """Tournament API."""
    @routes.post(prefix)
    async def _(request: web.Request):
        storage = request.app["storage"]
        body = await request.json()
        data = storage.save(Tournament.create(**body), **request.app)
        data = asdict((await data) if isawaitable(data) else data)
        return web.json_response(data)

    return routes

def main(application: web.Application):
    parser = ArgumentParser(description="Kicker application server")
    parser.add_argument("--assets", type=Path, required=True, help="Asset path")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    args = parser.parse_args()

    install(storage, into=application, under="storage")

    application.add_routes(profiles(web.RouteTableDef(), prefix="/profiles"))
    application.add_routes(teams(web.RouteTableDef(), prefix="/teams"))
    application.add_routes(memberships(web.RouteTableDef(), prefix="/memberships"))

    application.router.add_get("/", lambda req: web.FileResponse(args.assets / "index.html"))
    application.router.add_static("/static", args.assets)
    web.run_app(application, host=args.host)

if __name__ == "__main__":
    main(web.Application(middlewares=[normalize_path_middleware(append_slash=False, remove_slash=True), schema_validation_middleware]))