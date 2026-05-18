import numpy as np
import librosa as lb
from numpy import pi, cos, sin, exp
import matplotlib.pyplot as plt

def rectangular_window(n: float, L: int) -> float:
    """
    Returns the values of the rectangular window

    Args:
        n (int): Index of the rectangular window
        L (int): Window length

    Returns:
        float: The value of the rectangular window at n
    """
    if n >= 0 and n <= L - 1:
        return 1
    else:
        return 0

def bartlett_window(n: float, L: int) -> float:
    """
    Returns the values of the Bartlett window

    Args:
        n (int): Index of the Bartlett window
        L (int): Window length

    Returns:
        float: The value of the Bartlett window at n
    """
    if n >= 0 and n <= (L - 1)/2:
        return (2 * n) / (L - 1)
    elif n > (L - 1)/2 and n <= L - 1:
        return 2 - (2 * n) / (L - 1)
    else:
        return 0
    
def hamming_window(n: float, L: int) -> float:
    """
    Returns the values of the Hamming window

    Args:
        n (int): Index of the Hamming window
        L (int): Window length

    Returns:
        float: The value of the Hamming window at n
    """
    if n >= 0 and n <= L - 1:
        return 0.54 - 0.46 * cos((2*pi*n)/(L-1))
    else:
        return 0

def hann_window(n: float, L: int) -> float:
    """
    Returns the values of the Hann window

    Args:
        n (int): Index of the Hann window
        L (int): Window length

    Returns:
        float: The value of the Hann window at n
    """
    if n >= 0 and n <= L - 1:
        return 0.5 - 0.5 * cos((2 * pi * n) / (L - 1))
    else:
        return 0

def freq_rectangular_window(omega: float, L: int) -> complex:
    """
    Returns the DTFT of the rectangular windows at omega, given the window length L

    Args:
        omega (float): the variable for the function
        L (int): The window length

    Returns:
        complex: The value of the DTFT of the rectangular window at omega
    """
    if omega == 0:
        return L
    else:
        return exp((-1j) * omega * ((L-1)/2)) * (sin((omega * L) / 2) / sin(omega / 2))

def freq_bartlett_window(omega: float, L: int) -> complex:
    """
    Returns the DTFT of the bartlett windows at omega, given the window length L

    Args:
        omega (float): the variable for the function
        L (int): The window length

    Returns:
        complex: The value of the DTFT of the bartlett window at omega
    """    
    if omega == 0:
        return L/2
    else:
        return (2/L) * exp((-1j) * omega * ((L-1)/2)) * (sin((omega * L) / 4) / sin(omega / 2))**2

def freq_hamming_window(omega: float, L: int) -> complex:
    """
    Returns the DTFT of the hamming windows at omega, given the window length L

    Args:
        omega (float): the variable for the function
        L (int): The window length

    Returns:
        complex: The value of the DTFT of the hamming window at omega
    """
    
    part1 = 0.54 * freq_rectangular_window(omega, L)
    part2 = -0.23 * freq_rectangular_window(omega - (2 * pi)/(L-1), L)
    part3 = -0.23 * freq_rectangular_window(omega + (2 * pi)/(L-1), L)
    return part1 + part2 + part3

def freq_hann_window(omega: float, L: int) -> complex:
    """
    Returns the DTFT of the hann windows at omega, given the window length L

    Args:
        omega (float): the variable for the function
        L (int): The window length

    Returns:
        complex: The value of the DTFT of the hann window at omega
    """
    
    part1 = 0.5 * freq_rectangular_window(omega, L)
    part2 = -0.25 * freq_rectangular_window(omega - (2 * pi) / (L - 1), L)
    part3 = -0.25 * freq_rectangular_window(omega + (2 * pi) / (L - 1), L)
    return part1 + part2 + part3


L = 51
#n = np.arange(0,L)
n = np.linspace(-1,L, 1001)

rect = np.array([rectangular_window(i, L) for i in n])
bart = np.array([bartlett_window(i, L) for i in n])
hamm = np.array([hamming_window(i, L) for i in n])
hann = np.array([hann_window(i, L) for i in n])

plt.plot(n,rect, label = "Rectangular")
plt.plot(n,bart, label = "Bartlett")
plt.plot(n,hamm, label = "Hamming")
plt.plot(n,hann, label = "Hann")
plt.xlabel("n")
plt.ylabel("w(n)")
plt.grid()
plt.legend()
plt.title("Window functions in time of length 51")
plt.savefig("windows_time.png", dpi = 200)
plt.clf()



omega = np.linspace(0, pi, 500000)


freq_rect = np.array([freq_rectangular_window(i, L) for i in omega])
freq_bart = np.array([freq_bartlett_window(i, L) for i in omega])
freq_hamm = np.array([freq_hamming_window(i, L) for i in omega])
freq_hann = np.array([freq_hann_window(i, L) for i in omega])


abs_freq_rect = np.abs(freq_rect)
abs_freq_bart = np.abs(freq_bart)
abs_freq_hamm = np.abs(freq_hamm)
abs_freq_hann = np.abs(freq_hann)


db_freq_rect = lb.amplitude_to_db(abs_freq_rect, ref = np.max, top_db=80)
db_freq_bart = lb.amplitude_to_db(abs_freq_bart, ref = np.max, top_db=80)
db_freq_hamm = lb.amplitude_to_db(abs_freq_hamm, ref = np.max, top_db=80)
db_freq_hann = lb.amplitude_to_db(abs_freq_hann, ref = np.max, top_db=80)


plt.plot(omega, db_freq_rect, label = "Rectangular")
plt.plot(omega, db_freq_bart, label = "Bartlett")
plt.plot(omega, db_freq_hamm, label = "Hamming")
plt.plot(omega, db_freq_hann, label = "Hann")

plt.title("Window functions in frequency")
plt.xlabel("ω")
plt.ylabel("|W(e^jω)| [dBFS]")
plt.grid()
plt.legend()
plt.savefig("Windows_freq.png", dpi = 200)




