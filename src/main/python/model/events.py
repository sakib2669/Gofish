from dataclasses import dataclass
from typing import Callable, Union


@dataclass(eq=True, frozen=True)
class PlayerJoinEvent:
    player_num: int


@dataclass(eq=True, frozen=True)
class PlayerLeaveEvent:
    player_num: int


@dataclass(eq=True, frozen=True)
class PlayerNicknameEvent:
    player_num: int
    name: str


@dataclass(eq=True, frozen=True)
class PlayerChatEvent:
    player_num: int
    nickname: str
    message: str


GameEvent = Union[PlayerJoinEvent, PlayerLeaveEvent, PlayerChatEvent]
GameObserver = Callable[[GameEvent], None]
