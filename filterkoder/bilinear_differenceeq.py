import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

fs = 16000

b = [0.281, -0.281]
a = [1, -1.3981, 0.438]

w, H = signal.freqz(b, a, worN=4096, fs=fs)

gain = np.max(np.abs(H))
b_normalized = b / gain

w, H_normalized = signal.freqz(b_normalized, a, worN=4096, fs=fs)



# graf for impulse response
plt.figure()
plt.plot(w, np.abs(H_normalized))
plt.title('Magnitude of H(z)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show()

