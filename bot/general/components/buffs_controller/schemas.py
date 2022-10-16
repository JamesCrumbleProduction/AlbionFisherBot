from pydantic import BaseModel


class BuffConfig(BaseModel):

    name: str
    activation_key: str


class BuffInfo(BaseModel):
    name: str
    is_active: bool
    have_buff_item: bool
