from dataclasses import dataclass
import fastjsonschema

class _Tag:
    """Simple singleton base class, for usage with tag types."""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

@dataclass
class PlayerRequest:
    """Player request information."""

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    name: str

@dataclass
class Player:
    """Player objects."""

    class Index(_Tag):
        """Player index tag."""
    
    validate = staticmethod(fastjsonschema.compile({
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "location": {
                "type": "string",
                "enum": ["Berlin", "Munich", "Würzburg"]
            }
        },
        "required": ["name", "location"]
    }))

    @classmethod
    def create(cls, **kwargs):
        return cls(**cls.validate(kwargs))

    name: str
    location: str

@dataclass
class Team:
    """Team objects."""

    class Index(_Tag):
        """Team index tag."""

    validate = staticmethod(fastjsonschema.compile({
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            }
        },
        "required": ["name"]
    }))

    @classmethod
    def create(cls, **kwargs):
        return cls(**cls.validate(kwargs))

    name: str

@dataclass
class Membership:
    """Membership in a team."""
    validate = staticmethod(fastjsonschema.compile({
        "type": "object",
        "properties": {
            "player": {
                "member": "string"
            },
            "team": {
                "within": "string"
            }
        },
        "required": ["member", "within"]
    }))

    @classmethod
    def create(cls, **kwargs):
        return cls(**cls.validate(kwargs))

    member: str
    within: str

@dataclass
class Tournament:
    """Kicker tournament."""
    validate = staticmethod(fastjsonschema.compile({
        "type": "object",
        "properties": {
            "timestamp": {
                "type": "string",
                "format": "date-time"
            },
            "location": {
                "type": "string",
                "enum": ["Berlin", "Munich", "Würzburg"]
            },
            "mode": {
                "type": "string",
                "enum": ["one-match", "best-of-3", "best-of-5"]
            },
            "a": {
                "type": "string",
            },
            "b": {
                "type": "string"
            }
        },
        "required": ["timestamp", "location", "mode", "a", "b"]
    }))

    @classmethod
    def create(cls, **kwargs):
        return cls(**cls.validate(kwargs))

    when: str
    location: str
    mode: str
    a: str
    b: str

@dataclass
class Match:
    """Single match in a tournament."""
    validate = staticmethod(fastjsonschema.compile({
        "type": "object",
        "properties": {
            "a": {
                "type": "integer",
                "minimum": 0
            },
            "b": {
                "type": "integer",
                "minimum": 0
            }
        },
        "required": ["a", "b"]
    }))

    @classmethod
    def create(cls, **kwargs):
        return cls(**cls.validate(kwargs))

    a: int
    b: int