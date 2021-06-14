from dataclasses import asdict
import sqlite3
from functools import singledispatch
from typing import Any, Mapping

from kickerapp.domain import Membership, Player, PlayerRequest, Team, Tournament

async def on_startup(state: Mapping[str, Any]):
    state["db"] = sqlite3.connect(":memory:")
    state["db"].row_factory = sqlite3.Row
    state["db"].executescript("""
    PRAGMA foreign_keys = 1;
    CREATE TABLE player(name text PRIMARY KEY, location text);
    CREATE TABLE team(name text PRIMARY KEY);
    CREATE TABLE membership(
        within text,
        member text,
        FOREIGN KEY(within) REFERENCES team(name) ON DELETE CASCADE,
        FOREIGN KEY(member) REFERENCES player(name) ON DELETE CASCADE,
        PRIMARY KEY(within, member)
    );
    CREATE TABLE tournament(
        id integer PRIMARY KEY,
        timestamp string,
        location string,
        mode string,
        a string,
        b string
    );
    """)

async def on_cleanup(state: Mapping[str, Any]):
    if "db" in state:
        state["db"].close()
        del state["db"]

@singledispatch
def save(obj: Any, **kwargs):
    raise TypeError(f"Could not save object of unknown type: {obj!r}")

@singledispatch
def load(obj: Any, **kwargs):
    raise TypeError(f"Could not load object of unknown type: {obj!r}")

@singledispatch
def delete(obj: Any, **kwargs):
    raise TypeError(f"Could not load object of unknown type: {obj!r}")

#region Player persistency

@load.register
def _(obj: Player.Index, *, db: sqlite3.Connection, **kwargs):
    with db:
        items = [Player(**row) for row in db.execute("SELECT * FROM player")]
    return items

@save.register
def _(obj: Player, *, db: sqlite3.Connection, **kwargs):
    with db:
        try:
            db.execute("INSERT INTO player VALUES(:name, :location)", asdict(obj))
        except sqlite3.IntegrityError:
            db.execute("UPDATE player SET location = :location WHERE name = :name", asdict(obj))
    return obj

@load.register
def _(obj: PlayerRequest, *, db: sqlite3.Connection, **kwargs):
    with db:
        cursor = db.execute("SELECT * FROM player WHERE name = :name", asdict(obj))
        result = cursor.fetchone()
    if result is not None:
        return Player(**result)

@delete.register
def _(obj: PlayerRequest, *, db: sqlite3.Connection, **kwargs):
    with db:
        cursor = db.execute("DELETE FROM player WHERE name = :name", asdict(obj))
    return cursor.rowcount > 0

#endregion

#region Team persistency

@load.register
def _(obj: Team.Index, *, db: sqlite3.Connection, **kwargs):
    with db:
        items = [Team(**row) for row in db.execute("SELECT * FROM team")]
    return items

@save.register
def _(obj: Team, *, db: sqlite3.Connection, **kwargs):
    with db:
        cursor = db.execute("INSERT OR IGNORE INTO team VALUES(:name)", asdict(obj))
    if cursor.rowcount > 0:
        return obj

@delete.register
def _(obj: Team, *, db: sqlite3.Connection, **kwargs):
    with db:
        cursor = db.execute("DELETE FROM team WHERE name = :name", asdict(obj))
    return cursor.rowcount > 0

@save.register
def _(obj: Membership, with_deps=True, *, db: sqlite3.Connection, **kwargs):
    with db:
        if with_deps:
            save(Team(obj.within), db=db)
        try:
            cursor = db.execute("INSERT INTO membership VALUES(:within, :member)", asdict(obj))
        except sqlite3.IntegrityError:
            raise ValueError(f"Unknown player or team name")
    if cursor.rowcount > 0:
        return obj

#endregion

#region Tournament persistency

@save.register
def _(obj: Tournament, *, db: sqlite3.Connection, **kwargs):
    pass

#endregion