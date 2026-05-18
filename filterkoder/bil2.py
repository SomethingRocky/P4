import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

fs = 16000
f_1 = 150
f_2 = 2500

b,a = signal.butter(2, [f_1, f_2], fs=fs, btype='bandpass')

w, H = signal.freqz(b, a, worN=4096, fs=fs)

gain = np.max(np.abs(H))
b_normalized = b / gain

plt.figure()
plt.plot(w, np.abs(H))
plt.title('Magnitude of H(z)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.scatter(f_1, np.abs(H[np.argmin(np.abs(w - f_1))]), color='red', label='f_1 = 150 Hz')
plt.scatter(f_2, np.abs(H[np.argmin(np.abs(w - f_2))]), color='blue', label='f_2 = 2500 Hz')
plt.legend()
plt.show()



