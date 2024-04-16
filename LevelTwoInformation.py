from dataclasses import dataclass, field


@dataclass
class LevelTwoInformation:

    req_id: int = field(default=None)
    market_maker: str = field(default=None)
    position: int = field(default=None)
    operation: int = field(default=None)
    side: int = field(default=None)
    price: float = field(default=None)
    size: float = field(default=None)
    is_smart_depth: bool = field(default=None)




