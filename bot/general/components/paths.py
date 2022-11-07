import os

ROOT_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

ROTATIONS_FILE_PATH: str = os.path.join(ROOT_PATH, 'rotations.json')
LAST_LOCATION_FILE_PATH: str = os.path.join(ROOT_PATH, 'last_location.json')
