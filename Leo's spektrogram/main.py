import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

array, sampling_rate = librosa.load(librosa.ex("trumpet"))

S = librosa.feature.melspectrogram(y=array, sr=sampling_rate, n_mels=128, fmax=8000)
S_dB = librosa.power_to_db(S, ref=np.max)

plt.figure().set_figwidth(12)
librosa.display.specshow(
    S_dB,
    x_axis="time",
    y_axis="mel",
    sr=sampling_rate,
    fmax=8000,
    cmap="gray_r"    
    
)
plt.colorbar(format="%+2.0f dB")
plt.show()