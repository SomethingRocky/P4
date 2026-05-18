import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from scipy.signal import find_peaks
from scipy.io import wavfile

# dette program opstiller et IIr-filter ved hjælp af impuls invarians metoden, og plotter dets frekvensrespons

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
H_s = signal.TransferFunction(num, den)

#impuls invarians metoden
b, a, dt = signal.cont2discrete((num, den,), T, method='impulse')

#frekvensrespons for det digitale filter
w, h = signal.freqz(b.flatten(), a.flatten(), worN=1000)
f = w * fs / (2 * np.pi)  # Konvertering til frekvens i Hz

# normaliser gain
gain = np.max(np.abs(h))
b_normalized = b / gain

# ny frekvensrespons for det normaliserede filter
w, h = signal.freqz(b_normalized.flatten(), a.flatten(), worN=1000)
f = w * fs / (2 * np.pi)  # Konvertering til frekvens i Hz

# graf for båndpassfilteret
plt.figure()
plt.plot(f, np.abs(h))
plt.title('Magnitude of H(z) - normalized')
plt.xlabel('Frequency (Hz)')
plt.xlim(0, 3000)
plt.ylabel('Magnitude')
plt.grid(True)
plt.show()