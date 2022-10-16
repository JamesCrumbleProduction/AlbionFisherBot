from __future__ import annotations

from ..raw_templates import RawTemplates
from ..schemas import BuffCompiledTemplates
from ..template_compiler import TemplateCompiler
from ..structure import CompiledTemplates, BuffsCompiledTemplates


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
        self._status_bar_components = CompiledTemplates(TemplateCompiler(
            RawTemplates.FisherBotRawTemplates.status_bar_components
        ).compile_templates())
        self._buffs = BuffsCompiledTemplates([
            BuffCompiledTemplates(
                name=buff.name,
                item=[*TemplateCompiler([buff.item]).compile_templates()][0],  # noqa
                empty_slot=[*TemplateCompiler([buff.empty_slot]).compile_templates()][0],  # noqa
                is_active=list(CompiledTemplates(
                    TemplateCompiler(buff.is_active).compile_templates()
                ).templates)
            )
            for buff in RawTemplates.FisherBotRawTemplates.buffs
        ])
        self._other_templates = CompiledTemplates(TemplateCompiler(
            RawTemplates.FisherBotRawTemplates.other
        ).compile_templates())

    @property
    def bobbers(self) -> CompiledTemplates:
        return self._bobbers

    @property
    def status_bar_components(self) -> CompiledTemplates:
        return self._status_bar_components

    @property
    def buffs(self) -> BuffsCompiledTemplates:
        return self._buffs

    @property
    def other_templates(self) -> CompiledTemplates:
        return self._other_templates


FISHER_BOT_COMPILED_TEMPLATES = FisherBotCompiledTemplates()
