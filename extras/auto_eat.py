import time

from pynput.mouse import Button

from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

mouse_controller = MouseController()
keyboard_controller = KeyboardController()

time.sleep(5)

while True:
    keyboard_controller.press('2')
    keyboard_controller.release('2')
    time.sleep(1.1)
    mouse_controller.click(Button.right)
    time.sleep(0.1)
