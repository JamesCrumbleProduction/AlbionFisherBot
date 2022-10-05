from __future__ import annotations

from ..raw_templates import RawTemplates
from ..template_compiler import TemplateCompiler, CompiledTemplates


class FisherBotCompiledTemplates:

    _instance: FisherBotCompiledTemplates = None

    def __new__(cls: type[FisherBotCompiledTemplates], *args, **kwargs) -> FisherBotCompiledTemplates:
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):

        self._bobbers = CompiledTemplates(TemplateCompiler(
            RawTemplates.FisherBotRawTemplates.bobbers
        ).compile_templates())
        self._other_templates = CompiledTemplates(TemplateCompiler(
            RawTemplates.FisherBotRawTemplates.other
        ).compile_templates())

    @property
    def bobbers(self) -> CompiledTemplates:
        return self._bobbers

    @property
    def other_templates(self) -> CompiledTemplates:
        return self._other_templates


FISHER_BOT_COMPILED_TEMPLATES = FisherBotCompiledTemplates()
