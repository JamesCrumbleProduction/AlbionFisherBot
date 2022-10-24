from typing import Iterable, Iterator

from .schemas import CompiledTemplate, BuffCompiledTemplates


class CompiledTemplates:

    __slots__ = '_compiled_templates',

    def __init__(self, compiled_templates: Iterable[CompiledTemplate]):
        self._compiled_templates = {
            template.label: template
            for template in compiled_templates
        }

    def get(self, label: str) -> CompiledTemplate:
        return self._compiled_templates[label]

    @property
    def templates(self) -> Iterator[CompiledTemplate]:
        for template in self._compiled_templates.values():
            yield template


class BuffsCompiledTemplates:

    __slots__ = '_compiled_buffs'

    def __init__(self, buffs: Iterable[BuffCompiledTemplates]):
        self._compiled_buffs = {buff.name: buff for buff in buffs}

    def get(self, buff_name: str) -> BuffCompiledTemplates:
        return self._compiled_buffs[buff_name]

    @property
    def buffs(self) -> Iterator[BuffCompiledTemplates]:
        for buff in self._compiled_buffs.values():
            yield buff
