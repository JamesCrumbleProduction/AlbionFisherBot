from datetime import datetime
from pydantic import BaseModel

from ...components.buffs_controller import BuffInfo


class BotInfo(BaseModel):

    catched_fishes: int
    catching_errors: int
    skipped_non_fishes: int
    skipped_in_row: int
    session_start_datetime: datetime
    buffs: list[BuffInfo]
