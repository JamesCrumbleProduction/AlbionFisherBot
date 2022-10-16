from typing import Iterable
from pydantic import BaseModel


class RawTemplate(BaseModel):
    label: str
    path: str

    class Config:
        arbitrary_types_allowed = 'allow'


class BuffRawTemplates(BaseModel):

    name: str
    item: RawTemplate
    empty_slot: RawTemplate
    is_active: Iterable[RawTemplate]
