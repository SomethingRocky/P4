import numpy as np
import matplotlib.pyplot as plt
from numpy import pi, cos, sin, exp
from librosa import amplitude_to_db


def sinc(x: float | np.ndarray) -> float | np.ndarray:
    return np.sinc(x/pi)

def freq_to_omega(freq: float | np.ndarray, sr: float | int) -> float | np.ndarray:
    return 2 * pi * (freq / sr)
    
def bilinear_bandpass(omega: float | np.ndarray) -> complex | np.ndarray:
    z = exp(1j * omega)
    z = 1 / z
    b = 0.12584 - 0.25168 * (z ** 2) + 0.12584 * (z ** 4)
    a = 1 - 2.69136 * z + 2.70948 * (z ** 2) - 1.29657 * (z ** 3) + 0.2804 * (z ** 4)
    H = b / a
    return H

def imp_window_bandpass(n: int | np.ndarray, L: int, w1: float, w2: float) -> float | np.ndarray:
    if L % 2 == 0:
        a = L / 2
    else:
        a = (L - 1) / 2
    hd = (1 / pi) * (w2 * sinc(w2 * (n-a)) -w1 * sinc(w1 * (n-a)))
    whan = 1/2 - 1/2 * cos((2 * pi * n) / (L - 1))
    return hd * whan
    
def window_bandpass(omega: float | np.ndarray, L: int, w1: float, w2: float) -> complex | np.ndarray:
    omega = np.atleast_1d(omega)

    H = np.array([
        np.sum(
            np.array(
                [imp_window_bandpass(n, L, w1, w2) * exp(1j * omega_i * n) for n in range(L)]
                )) for omega_i in omega])
    return H

def findClosestWinFilt():
    #Filter Specifications
    sr = 16000
    f1 = 150
    f2 = 2500
    w1 = float(freq_to_omega(f1, sr))
    w2 = float(freq_to_omega(f2, sr))
    
    omega = np.linspace(0, pi, 10001)
    freqs = (omega / pi) * (sr / 2)
    
    Ls = [l for l in range(3, 202, 2)]
    for L in Ls:
        print(f"Checking L = {L}")
        Hw = window_bandpass(omega, L, w1, w2)
        Hw = np.abs(Hw)
        Hw_db = amplitude_to_db(Hw, ref = np.max)
        
        # Check specifications
        mask_0_100 = freqs <= 100
        spec1 = np.all(Hw_db[mask_0_100] <= -8)
        
        mask_4000_up = freqs >= 4000
        spec2 = np.all(Hw_db[mask_4000_up] <= -10)
        
        if spec1 and spec2:
            print(f"First L that meets specs: {L}")
            return L
        
    
    
def main():
    #Filter Specifications
    sr = 16000
    f1 = 150
    f2 = 2500
    w1 = float(freq_to_omega(f1, sr))
    w2 = float(freq_to_omega(f2, sr))
    L = 201
    
    omega = np.linspace(0, pi, 10001)
    freqs = (omega / pi) * (sr / 2)
    
    Hb = bilinear_bandpass(omega)
    Hw = window_bandpass(omega, L, w1, w2)
    Hb = np.abs(Hb)
    Hw = np.abs(Hw)
    topdb = 100
    Hbdb = amplitude_to_db(Hb, ref = 1, top_db = topdb)
    Hwdb = amplitude_to_db(Hw, ref = 1, top_db = topdb)
    
    plt.plot(freqs, Hbdb, label = "Bilinear method")
    plt.plot(freqs, Hwdb, label = f"Window method of {L-1}th order")
    #Cutoff frequency
    plt.hlines(-3.02, f1, f2, linestyles = "--", colors = "r")
    plt.vlines((f1, f2), -topdb, -3.02, linestyles = "--", colors = "r")
    
    #Gain specifications
    hz100 = -8
    hz4000 = -10
    plt.hlines((hz100, hz4000),(0, 4000),(100, sr/2), colors = "black")
    plt.vlines((100, 4000), (hz100, hz4000), (10,10), colors = "black")
    
    plt.title("Bilinear vs Window method")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("|H(e^jω)| [dBFS]")
    plt.xlim(0,sr/2)
    plt.ylim(-topdb, 2)
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    #findClosestWinFilt()
    main()
