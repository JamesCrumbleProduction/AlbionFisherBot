import wave
import pyaudio  # type: ignore

wf = wave.open("record.wav", "rb")
amountFrames = 100  # just an arbitrary number; could be anything
sframes = wf.readframes(amountFrames)

currentSoundFrame = 0

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 3

p = pyaudio.PyAudio()  # Create an interface to PortAudio
stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True, input_device_index=1)

# Store data in chunks for 3 seconds
for i in range(0, int(fs / chunk * seconds)):
    data = stream.read(chunk)

    # for i, j in zip(data, sframes):
    #     print(i, j)

    if data == sframes[currentSoundFrame]:
        currentSoundFrame += 1
        print(currentSoundFrame, len(sframes))
        if currentSoundFrame == len(sframes):  # the whole entire sound was played
            print("Sound was played!")


# Stop and close the stream
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
p.terminate()
