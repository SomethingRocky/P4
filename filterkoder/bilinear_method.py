import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from scipy.signal import find_peaks
from scipy.io import wavfile


# dette program opstiller et IIr-filter ved hjælp af bilinear metoden, og plotter dets frekvensrespons

#båndpassspecifikationer
fs = 16000
f_1 = 150
f_2 = 2500
T = 1/fs



omega_1 = 2 * np.pi * f_1
omega_2 = 2 * np.pi * f_2
Bredde = omega_2 - omega_1
omega_0 = np.sqrt(omega_1 * omega_2)

#opstiler tæller og nævner
num = [Bredde, 0]
den = [1, Bredde, omega_0**2]

#båndpassfilteret i s-domænet
H_s = num, den

#bilinear metoden
b, a = signal.bilinear(num, den, fs)

#frekvensrespons for det digitale filter
w, h = signal.freqz(b, a, worN=1000)
f = w * fs / (2 * np.pi)  # Konvertering til frekvens i Hz

# graf for båndpassfilteret
plt.figure()
plt.plot(f, np.abs(h))
plt.title('Magnitude of H(z)')
plt.xlabel('Frequency (Hz)')
plt.xlim(0, 3000)
plt.ylabel('Magnitude')
plt.grid(True)
plt.scatter(f_1, np.abs(h[np.argmin(np.abs(f - f_1))]), color='red', label='f_1 = 150 Hz')
plt.scatter(f_2, np.abs(h[np.argmin(np.abs(f - f_2))]), color='blue', label='f_2 = 2500 Hz')
plt.legend()
plt.show()