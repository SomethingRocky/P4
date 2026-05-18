import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from scipy.signal import find_peaks
from scipy.io import wavfile


#dette program opstiller et FIR-filter ved hjælp af vinduesmetoden, og plotter dets frekvensrespons

# indlæs en lydfil fra mappen "dronelyde" og opret en tidsvektor baseret på samplingfrekvensen
fs1, x1 = wavfile.read("dronelyde\\B_S2_D1_101-bebop_004_.wav")
t1 = np.arange(len(x1)) / fs1  # Tidsvektor baseret på samplingfrekvensen


# indlæs en anden lydfil fra mappen "lyde" og opret en tidsvektor baseret på samplingfrekvensen
fs2, x2 = wavfile.read("lyde\\2-42101-A-430.wav")
t2 = np.arange(len(x2)) / fs2  # Tidsvektor baseret på samplingfrekvensen

if fs1 != fs2:
    raise ValueError("Samplingfrekvenserne for de to signaler er ikke ens. Vælg signaler med samme samplingfrekvens.")

# kombiner de to signaler ved at tilføje dem sammen
min_len = min(len(x1), len(x2))  # Find den mindste længde af de to signaler
x = x1[:min_len] + x2[:min_len]  # Kombiner signalerne ved at tilføje dem sammen

#båndpassspecifikationer
fs = fs1 # Samplingfrekvens (antaget at begge signaler har samme samplingfrekvens)
f_1 = 150
f_2 = 2500
T = 1/fs
omega_1 = 2 * np.pi * f_1
omega_2 = 2 * np.pi * f_2
Bredde = omega_2 - omega_1
omega_0 = np.sqrt(omega_1 * omega_2)
#båndpassfilteret i s-domænet

#vinduesmetoden
N = 201  # Filterlængde
h = signal.firwin(N, [f_1, f_2], pass_zero=False,fs = fs, window='hann',)

#frekvensrespons for det digitale filter
w, H = signal.freqz(h, worN=1000)
f = w * fs / (2 * np.pi)  # Konvertering til frekvens i Hz

y = signal.lfilter(h, 1, x)  # Filtrer det originale signal


# ny tidsvektor for det kombinerede signal
t = np.arange(len(x)) / fs

#fft plot for det originale og filtrerede signal
X = np.fft.fft(x)
Y = np.fft.fft(y)
f_fft = np.fft.fftfreq(len(x), T)
mask = f_fft >= 0  # Kun positive frekvenser

X_norm = 2 * np.abs(X[mask]) / len(x) # Normaliser det originale signal
Y_norm = 2 * np.abs(Y[mask]) / len(y)  # Normaliser det filtrerede signal



# plot af det originale og filtrerede signal i frekvensdomænet
plt.figure()
plt.subplot(2, 1, 1)
plt.plot(f_fft[mask], X_norm, label='Original Signal')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(0, 4000)
plt.grid(True)
plt.subplot(2, 1, 2)
plt.plot(f_fft[mask], Y_norm, label='Filtered Signal')
plt.title('Magnitude Spectrum of Filtered Signal')
plt.xlabel('Frequency (Hz)')
plt.xlim(0, 4000)
plt.ylabel('Magnitude')
plt.grid(True)
plt.tight_layout()
plt.show()

# graf for båndpassfilteret
plt.figure()
plt.plot(f, np.abs(H))
plt.title('Magnitude of H(z)')
plt.xlabel('Frequency (Hz)')
plt.xlim(0, 4000)
plt.ylabel('Magnitude')
plt.grid(True)
plt.savefig("Ababdpass",dpi=400)
plt.show()

#plot i dB
plt.figure()
plt.plot(f, 20 * np.log10(np.maximum(np.abs(H), 1e-10)))  # Undgå log(0) ved at sætte en minimumsværdi
plt.title('Magnitude of H(z) in dB')
plt.xlabel('Frequency (Hz)')
plt.xlim(0, 4000)
plt.ylim(-100,5)
plt.scatter((10, 150, 1940 , 2500),(-30,-1,-1,-60), marker="x", color="red")
plt.ylabel('Magnitude (dB)')
plt.grid(True)
plt.savefig("dbbandpass",dpi=400)
plt.show()
