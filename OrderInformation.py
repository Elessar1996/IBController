from dataclasses import dataclass, field


@dataclass

class OrderInformation:

    orderId: int = field(default=None)
    status: str = field(default=None)
    filled: float = field(default=None)
    remaining: float = field(default=None)
    avgFillPrice: float = field(default=None)
    permId: int = field(default=None)
    parentId: int = field(default=None)
    lastFillPrice: int = field(default=None)
    clientId: int = field(default=None)
    whyHeld: str = field(default=None)
    mktCapPrice: float = field(default=None)