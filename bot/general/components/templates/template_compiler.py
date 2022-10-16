import os
import cv2

from numpy import ndarray
from typing import Iterable, Iterator

from .schemas import CompiledTemplate
from .raw_templates.schemas import RawTemplate


def to_cvt_color(raw_image: ndarray) -> ndarray:
    return cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)


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


class TemplateCompiler:

    __slots__ = '_raw_templates',

    def __init__(self, raw_templates: Iterable[RawTemplate]):
        self._raw_templates = raw_templates

    def compile_templates(self) -> Iterator[CompiledTemplate]:
        for template in self._validate_images_paths(self._raw_templates):
            yield CompiledTemplate(
                label=template.label,
                template_data=self._image_serializer(template)
            )

    def _image_serializer(
        self,
        valided_template: RawTemplate
    ) -> ndarray:
        return to_cvt_color(cv2.imread(valided_template.path))

    def _validate_images_paths(self, raw_templates: Iterable[RawTemplate]) -> Iterator[RawTemplate]:
        for template in raw_templates:
            if os.path.exists(template.path) and os.path.isfile(template.path):
                yield template
            else:
                raise NotImplementedError(
                    f'Template with {template.label} label have uncorrected path: \n\t => {template.path}'
                )
