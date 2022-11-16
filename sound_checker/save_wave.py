import wave
import pyaudio

from typing import Any


DEBUG: bool = False
DEVICE_NAME: str = 'Line 1 (Virtual Audio Cable)'

CHUNK: int = 1024
RECORD_SECONDS: int = 5
SAMPLE_FORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()

print('Trying to find virtual device cable')

for i in range(p.get_device_count()):
    device: dict[str, Any] = p.get_device_info_by_index(i)  # type: ignore

    device_index: int = i
    sample_rate: int = int(device['defaultSampleRate'])
    device_name: str = device['name']
    channels: int = device['maxInputChannels']

    if device_name == DEVICE_NAME and channels == 2:
        print(f'\n\nFOUND NEEDED "{DEVICE_NAME}" DEVICE')
        print(device)
        break

    print(device)
else:
    raise ValueError(f'CANNOT FIND "{DEVICE_NAME}" DEVICE')


frames: list[bytes] = list()
stream = p.open(
    format=SAMPLE_FORMAT,
    channels=channels,
    rate=sample_rate,
    frames_per_buffer=CHUNK,
    input=True,
    input_device_index=device_index,
)

print('Recording')

# Store data in chunks for 3 seconds
for _ in range(0, int(sample_rate / CHUNK * RECORD_SECONDS)):
    data: bytes = stream.read(CHUNK)

    if DEBUG:
        print(data)

    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

print('Finished recording')

with wave.open('record.wav', 'wb') as wave_handle:
    wave_handle.setnchannels(channels)
    wave_handle.setsampwidth(p.get_sample_size(SAMPLE_FORMAT))
    wave_handle.setframerate(sample_rate)
    wave_handle.writeframes(b''.join(frames))
