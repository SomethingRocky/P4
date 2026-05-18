import numpy as np
import librosa as lb
import librosa.display
from numpy import pi, sin
import matplotlib.pyplot as plt

sample_freq = 24e3 #Hz
sample_time = 1/sample_freq #seconds
signal_length: float = 30 #seconds
samples = int(signal_length / sample_time)

t = np.array([i*sample_time for i in range(samples)])
signal = sin(1000 * t**2)

u = np.zeros_like(t)
u[:samples//2] = t[:samples//2]
signal += sin(2 * pi * 2000 * u)

windows = ["rectangular", "bartlett", "hann", "hamming"]
titles = ["Rectangular", "Bartlett", "Hann", "Hamming"]
window_Length = 256
hop_length = window_Length//4 #c in our project

fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True, sharey=True)

mappable = None
for ax, window, title in zip(axes.ravel(), windows, titles):
    stft = lb.stft(signal, window=window, n_fft=window_Length, hop_length=hop_length)
    stft_db = lb.amplitude_to_db(np.abs(stft) ** 2, ref=np.max, top_db=120)
    mappable = lb.display.specshow(stft_db, x_axis="time", y_axis="hz", ax=ax, sr=sample_freq, hop_length=hop_length)
    ax.set_title(title)

fig.subplots_adjust(left=0.07, right=0.9, bottom=0.08, top=0.93, wspace=0.10, hspace=0.22)
fig.colorbar(mappable, ax=axes.ravel().tolist(), format="%+2.0f dB", pad=0.01, fraction=0.03) # type: ignore
plt.savefig("Window spectrograms.png", dpi = 200)
plt.xlim(3,10)
plt.ylim(500,3000)
plt.savefig("Window spectrograms zoomed.png", dpi = 200)




