import time
import httpx
import orjson
import threading
import tkinter as tk

from typing import Any
from fastapi import Request


class Panel:

    def __init__(self):
        self.is_running: bool = True
        self.window = tk.Tk()
        self.window.geometry('600x600')

        self.label = tk.Label(text='', background='gray')
        self.label.pack()

        self._machines: dict[str, str] = dict()
        self._machines_info: dict[str, dict[str, Any]] = dict()

    def _update_label_text(self) -> None:
        self._update_machines_info()
        self.label.config(text=self._machines_info_to_text())

    def _machines_info_to_text(self) -> str:
        text_buffer: str = ''

        for vm_name, machine_info in self._machines_info.items():
            current_location = machine_info["current_location"] if machine_info["current_location"] != '' else 'WITHOUT ROTATIONS'
            text_buffer += f'{vm_name} -> in "{current_location}" location with "{machine_info["status"]}" status\n'  # noqa
            text_buffer += f'{" " * len(vm_name)}    ' + f'{" " * len(vm_name)}    '.join([
                f"catched_fishes -> {machine_info['bot_info']['catched_fishes']}",
                f"catching_errors -> {machine_info['bot_info']['catching_errors']}",
                f"skipped_non_fishes -> {machine_info['bot_info']['skipped_non_fishes']}",
                f"skipped_non_fishes -> {machine_info['bot_info']['skipped_non_fishes']}",
            ])
            text_buffer += '\n'

        return text_buffer

    def _update_machines_info(self) -> None:
        machines_info: dict[str, dict[str, Any]] = dict()

        for vm_name, destination in self._machines.items():
            try:
                info_destination = destination + '/bot_info'

                status_destination = info_destination + '/status'
                bot_info_destination = info_destination + '/info'
                current_location_destination = info_destination + '/current_location'

                print(info_destination)

                with httpx.Client() as client:
                    machines_info[vm_name] = dict()

                    machines_info[vm_name]['status'] = client.get(status_destination, timeout=1).text
                    machines_info[vm_name]['bot_info'] = orjson.loads(client.get(bot_info_destination, timeout=1).text)
                    machines_info[vm_name]['current_location'] = client.get(current_location_destination, timeout=1).text
            except Exception as exception:
                print(f'EXCEPTION WHEN TRYING GET INFO ABOUT "{vm_name}" FROM SERVER => {exception}')
                del machines_info[vm_name]

        self._machines_info = machines_info

    def register_machine(self, vm_name: str, port: int, request: Request) -> None:
        if vm_name not in self._machines:
            self._machines[vm_name] = f'http://{request.client.host}:{port}'  # type: ignore

    def _inf_polling_machines(self) -> None:
        while True:
            self._update_label_text()
            time.sleep(5)

    def run(self) -> None:
        threading.Thread(target=self._inf_polling_machines).start()
        self.window.mainloop()


PANEL = Panel()
