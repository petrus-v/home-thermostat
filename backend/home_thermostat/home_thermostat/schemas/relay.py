from pydantic import BaseModel
from typing import Optional


class RelayState(BaseModel):
    is_open: bool = False
    """Tell whatever the network is open (turned off) or closed (turned off)
    """

    def __eq__(self, other: "RelayState") -> bool:
        return self.is_open == other.is_open
