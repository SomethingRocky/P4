import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

array, sampling_rate = librosa.load(librosa.ex("trumpet"))


""" plt.figure().set_figwidth(12)
librosa.display.waveshow(array, sr=sampling_rate)
plt.ylabel("Relative amplitude")
plt.xlabel("Time [s]")
plt.show() """

dft_input = array[:]


# calculate the DFT
window = np.hanning(len(dft_input))
windowed_input = dft_input * window


dft = np.fft.rfft(windowed_input)


# get the amplitude spectrum in decibels
amplitude = np.abs(dft)
amplitude_db = librosa.amplitude_to_db(amplitude, ref=np.max)

# get the frequency bins
frequency = librosa.fft_frequencies(sr=sampling_rate, n_fft=len(dft_input))


plt.figure().set_figwidth(12)
plt.plot(frequency, amplitude_db)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (dBFS)")
#plt.xscale("log")
plt.show()


""" #Frequency spectrum of the first note
dft_input_small = array[:4096]


# calculate the DFT
window = np.hanning(len(dft_input_small))
windowed_input = dft_input_small * window


dft = np.fft.rfft(windowed_input)


# get the amplitude spectrum in decibels
amplitude = np.abs(dft)
amplitude_db = librosa.amplitude_to_db(amplitude, ref=np.max)

# get the frequency bins
frequency = librosa.fft_frequencies(sr=sampling_rate, n_fft=len(dft_input_small))
fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

# Left: magnitude spectrum
axes[0].plot(amplitude_db, frequency)
axes[0].set_xlabel("Amplitude (dB)")
axes[0].set_ylabel("Frequency (Hz)")
axes[0].set_title("Frequency spectrum (First note)")
axes[0].grid()



#Spectrogram
D = librosa.stft(array)
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

# Right: spectrogram
img = librosa.display.specshow(S_db, x_axis="time", y_axis="hz", ax=axes[1])
axes[1].set_title("Spectrogram")
axes[1].set_ylabel("")
fig.colorbar(img, ax=axes[1], format="%+2.0f dB")

plt.tight_layout()
plt.show() """

""" S = librosa.feature.melspectrogram(y=array, sr=sampling_rate, n_mels=128, fmax=8000)
S_dB = librosa.power_to_db(S, ref=np.max)

plt.figure().set_figwidth(12)
librosa.display.specshow(S_dB, x_axis="time", y_axis="mel", sr=sampling_rate, fmax=8000)
plt.colorbar()
plt.show()  """

