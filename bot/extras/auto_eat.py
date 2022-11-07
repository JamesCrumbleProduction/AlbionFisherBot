import time

from pynput.mouse import Button

from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

mouse_controller = MouseController()
keyboard_controller = KeyboardController()

time.sleep(2.5)

mouse_position = mouse_controller.position
print('MOUSE POSITION WAS SAVED')

time.sleep(2.5)

while True:
    if mouse_controller.position[0] != mouse_position[0] or mouse_controller.position[1] != mouse_position[1]:
        mouse_controller.position = mouse_position
    keyboard_controller.press('2')
    keyboard_controller.release('2')
    time.sleep(1.1)
    mouse_controller.click(Button.right)
    time.sleep(0.1)
