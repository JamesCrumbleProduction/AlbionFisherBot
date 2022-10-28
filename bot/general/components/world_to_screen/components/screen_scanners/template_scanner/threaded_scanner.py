from typing import Iterator
from concurrent.futures import Future

from .sync_scanner import TemplateScanner
from ...helpers import source_auto_update
from ....schemas import Coordinate, Region
from ......services.executor import SCANNER_EXECUTOR


class ThreadedTemplateScanner(TemplateScanner):

    @source_auto_update
    def iterate_all_by_first_founded(self) -> Iterator[Coordinate | None]:

        i: int = 0
        futures: list[Future] = list()

        while i < len(self.templates):
            if len(futures) < SCANNER_EXECUTOR._max_workers:
                future = SCANNER_EXECUTOR.submit(
                    self._validate_template, self.templates[i]
                )
                i = i + 1
                futures.append(future)

            for j, future in enumerate(futures):
                if future.done():
                    if template_data := future.result():
                        yield Coordinate(
                            x=(
                                template_data.location_x[0]
                                + template_data.width // 2
                                + self._image.region.left
                            ),
                            y=(
                                template_data.location_y[0]
                                + template_data.height // 2
                                + self._image.region.top
                            ),
                            region=Region(
                                width=template_data.width,
                                height=template_data.height,
                                left=self._image.region.left + template_data.location_x[0],  # noqa
                                top=self._image.region.top + template_data.location_y[0]  # noqa
                            )
                        )
                    else:
                        yield None

                    futures.pop(j)
                    break

    @source_auto_update
    def get_condition_by_one(self) -> bool:
        for coordinate in self.iterate_all_by_first_founded():
            if coordinate is not None:
                return True

        return False

    @source_auto_update
    def iterate_one_by_each_founded(self) -> Iterator[Coordinate]:
        raise NotImplementedError()

    @source_auto_update
    def iterate_all_by_each_founded(self) -> Iterator[Coordinate]:
        raise NotImplementedError()

    @source_auto_update
    def indentify_by_first(self) -> Coordinate | None:
        raise NotImplementedError()
