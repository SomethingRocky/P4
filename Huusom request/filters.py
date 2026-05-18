import numpy as np
import scipy as scp
from librosa import amplitude_to_db
from droneDetection import load_audio
import matplotlib.pyplot as plt

def average_filter(signal: np.ndarray, N: int) -> np.ndarray:
    """
    Takes a signal and applies the N'th order averaging filter.
    Works with both 1D signals and 2D arrays (applies filter along last axis).

    Args:
        signal (np.ndarray): The signal which is to be applied the averaging filter
        N (int): The order of the averaging filter

    Returns:
        np.ndarray: The filtered signal
    """
    h = np.ones(N) / N
    
    # Handle 2D arrays (e.g., STFT spectrograms)
    if signal.ndim == 2:
        filtered = np.zeros_like(signal)
        for i in range(signal.shape[0]):
            filtered[i] = np.convolve(signal[i], h, "same")
        return filtered
    else:
        return np.convolve(signal, h, "same")

def scp_window_filter(signal: np.ndarray, 
                     sr: float,
                     N: int, 
                     cutoff: float | list, 
                     type: str, 
                     window: str
                     ) -> np.ndarray:
    h = scp.signal.firwin(N, cutoff, pass_zero = type,  window = window, fs = sr)
    if __name__ == "__main__":
        plt.plot(h)
        plt.show()
        plt.clf()
        H = np.fft.rfft(h)
        H = np.abs(H)
        Hdb = amplitude_to_db(H)
        freqs = np.fft.rfftfreq(N, 1/sr)
        plt.plot(freqs, Hdb)
        plt.show()
        plt.clf()
    return np.convolve(signal, h, "same")

if __name__ == "__main__":
    signal, sr, filename = load_audio("drone")
    x = scp_window_filter(signal, sr = sr, N = 201, cutoff= [150, 2500], type = "bandpass", window = "hann")
    
    