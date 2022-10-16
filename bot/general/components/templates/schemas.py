from numpy import ndarray
from pydantic import BaseModel


from .raw_templates import BuffRawTemplates


class CompiledTemplate(BaseModel):
    label: str
    template_data: ndarray

    class Config:
        arbitrary_types_allowed = 'allow'


class BuffCompiledTemplates(BuffRawTemplates):

    item: CompiledTemplate
    empty_slot: CompiledTemplate
    is_active: list[CompiledTemplate]

    class Config:
        arbitrary_types_allowed = 'allow'
