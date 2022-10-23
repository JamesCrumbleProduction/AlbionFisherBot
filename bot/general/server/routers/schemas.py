from datetime import datetime
from pydantic import BaseModel


class BotInfo(BaseModel):

    catched_fishes: int
    catching_errors: int
    skipped_non_fishes: int
    session_start_datetime: datetime
