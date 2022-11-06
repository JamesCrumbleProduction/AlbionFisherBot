class RotationsReader:

    def __init__(self):
        self._locations: dict[str, int] = dict()

    @property
    def locations(self) -> list[str]:
        return [location for location in self._locations]


class Rotations:

    __slots__ = (
        '_current_location',
        '_reader',
    )

    def __init__(self, current_location: str, reader: RotationsReader):
        self._current_location: str = current_location
        self._reader = reader

    def resolve_path(self, location_key: str) -> None:
        ...
        # prev_time: float = 0
        # record = path['record']
        # catching_area = path['catching_point_catching_region']

        # time.sleep(5)

        # for i, moving in enumerate(record):
        #     print(moving)
        #     if i == 0:
        #         prev_time = moving[2]
        #         MOUSE.position = (moving[0], moving[1])
        #         MOUSE.press(Button.left)
        #     else:
        #         MOUSE.position = (moving[0], moving[1])

        #     time.sleep(moving[2] - prev_time)
        #     prev_time = moving[2]

        # MOUSE.release(Button.left)
