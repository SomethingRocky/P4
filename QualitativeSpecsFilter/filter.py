import numpy as np
from scipy.signal import firwin, convolve
import matplotlib.pyplot as plt

def scp_window_filter(signal: np.ndarray,
                      sr: float | int,
                      N: int,
                      cutoff: list,
                      type: str,
                      window: str = "hann",
                      ):
    h = firwin(N, cutoff = cutoff, pass_zero = type, window = window, fs = sr) #type: ignore
    if __name__ == "__main__":
        plt.plot(h)
        plt.show()
        plt.clf()
        H = np.fft.rfft(h)
        H = np.abs(H)
        freqs = np.fft.rfftfreq(len(h), 1/sr)
        plt.plot(freqs, H)
        plt.show()
        plt.clf()
    return convolve(signal, h, mode="same")

if __name__ == "__main__":
    import os
    import librosa as lb
    path = os.path.join("data","Binary_Drone_Audio","yes_drone","B_S2_D1_067-bebop_000_.wav")
    signal, sr = lb.load(path, sr = None)
    filtered_signal = scp_window_filter(
        signal,
        sr,
        N=201,
        cutoff=[150,2600],
        type="bandpass",
        window="hann",
    )
    
