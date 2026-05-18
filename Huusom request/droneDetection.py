import os
import numpy as np
import librosa as lb
from scipy import signal as scp
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from filters import *

#Definerer paths til mine data
data_path = "data"
drone_folder_name = "drone"
drone_path = os.path.join(data_path, drone_folder_name)
noise_folder_name = "noise"
noise_path = os.path.join(data_path, noise_folder_name)

# Map audio type to path
audio_paths = {
    "drone": drone_path,
    "noise": noise_path
}

#laver en list med navnene på alle drone og noise filer
drone_files = os.listdir(drone_path)
noise_files = os.listdir(noise_path)

# Dictionary to map audio type to file list
audio_files = {
    "drone": drone_files,
    "noise": noise_files
}


def load_audio(
    audio_type: str,
    SNR_db: float | None = None,
) -> tuple:
    """
    Loads the audio type, either drone or noise, adds noise with the given SNR,
    or none if no SNR is specified.

    Args:
        audio_type (str): either "drone" or "noise"
        SNR_db (_type_, optional): The signal to noise desired. Defaults to None.

    Returns:
        tuple (np.ndarray, float, str): Returns the audio file array, sample rate and name of the file 
        i.e. (signal, sample_rate, ) 
    """
    
    audio_file_name = np.random.choice(audio_files[audio_type])    
    signal, sr = lb.load(os.path.join(audio_paths[audio_type], audio_file_name), sr=None)
    
    #if SNR_db is given, add noise at given SNR
    if SNR_db != None:
        # Calculate signal power
        signal_power = np.mean(signal ** 2)
        
        # Load random noise file
        noise_file_name = np.random.choice(noise_files)
        noise, _ = lb.load(os.path.join(noise_path, noise_file_name), sr=sr)
        
        # Ensure noise has the same length as signal
        if len(noise) > len(signal):
            noise = noise[:len(signal)]
        elif len(noise) < len(signal):
            # Repeat noise to match signal length
            repeat_count = (len(signal) // len(noise)) + 1
            noise = np.tile(noise, repeat_count)[:len(signal)]
        
        # Calculate desired noise power from SNR_db formula: SNR = 20*log10(P_signal / P_noise)
        noise_power = signal_power / (10 ** (SNR_db / 20))
        
        # Scale noise to have the desired power
        current_noise_power = np.mean(noise ** 2)
        
        # Avoid division by zero
        if current_noise_power > 0:
            noise_scaled = noise * np.sqrt(noise_power / current_noise_power)
        else:
            noise_scaled = np.zeros_like(noise)
        
        # Add noise to signal
        noisy_signal = signal + noise_scaled
        
        # Normalizing to avoid clipping
        max_val = np.max(np.abs(noisy_signal))
        if max_val > 0:
            noisy_signal = noisy_signal / max_val
        
        return noisy_signal, sr, audio_file_name
    else:
        return signal, sr, audio_file_name

def find_f0(signal: np.ndarray, 
            sr: float, 
            prominence: float, 
            freq_bins: int,
            bin_tolerance: int = 20, 
            min_length:int = 4
            ) -> float | None:
    """
    Takes a signal and returns the most likely fundamental frequency of the signal.

    Args:
        signal (np.ndarray): A 1d array that is to be analyzed
        sr (float): The sample rate of the signal
        prominence (float): The prominence used for the scipy find_peaks function
        freq_bins (int): The amount of frequency bins
        bin_tolerance (int, optional): The tolerance of how close in bins, 
        the diff in peaks is allowed to be considered close to eachother. Defaults to 20.
        min_length (int, optional): The minimum amount of fundamental peaks needed,
        to classify it as harmonic. Defaults to 4.

    Returns:
        float | None: Returns the most likely fundamental frequency, but returns None if there is no likely candidate.
    """
    peaks, _ = find_peaks(signal, prominence = prominence)
    peaksdiff = np.diff(peaks)
    
    peaksdiffdiff = np.diff(peaksdiff)
    within_tol = np.abs(peaksdiffdiff) <= bin_tolerance
    
    #Padding to handle edge cases
    padded = np.concatenate(([False], within_tol, [False]))
    edges = np.where(np.diff(padded.astype(int)))[0]
    
    #Initalizing for loop
    longest = None
    longest_len = 0
    
    for i in range(0, len(edges), 2):
        start = edges[i]
        end = edges[i+1] if i+1 < len(edges) else len(peaksdiff)
        length = end - start
        if length >= min_length and length > longest_len:
            longest = peaksdiff[start:end]
            longest_len = length
            
    if longest is None:
        return None
    
    f0 = np.mean(longest) * ((sr/2) / freq_bins)
    
    return float(f0)

def harmonic_check(freqs: np.ndarray, 
                   peaks: np.ndarray, 
                   f0: float, 
                   num_to_true: int = 3, 
                   freq_tolerance_hz: float=50
                   ) -> bool:
    """
    Takes a fundamental frequency and checks if the signal is harmonic with that frequency.

    Args:
        freqs (np.ndarray): The frequency axis of the signal
        peaks (np.ndarray): The peaks of the signal
        f0 (float): The fundamental frequency of the signal
        num_to_true (int, optional): The amount of harmonic peaks needed to return True. Defaults to 3.
        freq_tolerance_hz (float, optional): The tolerance in frequency. Defaults to 50.

    Returns:
        bool: Returns True if the signal is harmonic with the given frequency.
    """
    if len(peaks) == 0:
        return False
    
    peak_freqs = freqs[peaks]
    num_harmonic_freqs = 0
    
    for i in range(2, 9):
        expected_harmonic = i * f0
        closest_peak = peak_freqs[np.argmin(np.abs(peak_freqs - expected_harmonic))]
        if np.abs(closest_peak - expected_harmonic) <= freq_tolerance_hz:
            num_harmonic_freqs += 1
    
    return num_harmonic_freqs >= num_to_true

def main(
    signal: np.ndarray,
    sr: float,
    filename: str,
    avg_filter_order: int = 5,
    window_type: str = "hann",
    window_length: int = 2048,
    hop_length: int | None = None,
    correlate_mode: str = "full",
    peak_f0_prominence: float = 0.06,
    peak_auto_prominence: float = 0.5,
    peak_auto_distance: int = 10,
    true_rate_succes: float = 0.6
) -> bool:
  
    # Adjust window_length if signal is too short
    if len(signal) < window_length:
        window_length = max(256, len(signal) // 2)
    
    if hop_length == None:
        hop_length = window_length // 4
    X = lb.stft(signal, 
                n_fft = window_length, 
                hop_length = hop_length, 
                window = window_type)
    freqs = lb.fft_frequencies(sr = sr, n_fft= window_length)
    
    #Filtering the frequency response to reduce noise in the spectrum
    X = np.abs(X)
    X = X - np.mean(X)
    X = average_filter(X, N = avg_filter_order)
    
    Hauto_shape = np.correlate(X[:,0], X[:,0], mode=correlate_mode).shape[0] #type:ignore
    Xauto = np.zeros((Hauto_shape, X.shape[1]))
    
    f0_list = []
    peaks = []
    
    for i in range(X.shape[1]):
        Xauto[:,i] = np.correlate(X[:,i],X[:,i], mode=correlate_mode) #type:ignore
        #Normalizing to have consistency over data
        max_val = np.max(Xauto[:,i])
        #and avoiding division by zero
        if max_val > 0:
            Xauto[:,i] = Xauto[:,i] / max_val
        else:
            Xauto[:,i] = np.zeros_like(Xauto[:,i])
        f0_list.append(find_f0(Xauto[:, i], 
                          sr, 
                          peak_f0_prominence, 
                          len(freqs),))
        peaksPlaceholder, _ = find_peaks(X[:,0], 
                                         prominence = peak_auto_prominence, 
                                         distance = peak_auto_distance)
        peaks.append(peaksPlaceholder)
    
    drones_bool = []
    for idx, f0 in enumerate(f0_list):
        if f0 is not None and 50 < f0 < 800:
            drones_bool.append(harmonic_check(freqs, peaks[idx], f0))
    
    
    if len(drones_bool) > 0:
        true_rate = sum(drones_bool) / len(drones_bool)
    else:
        return False
    
    if true_rate >= true_rate_succes:
        return True
    return False

if __name__ == "__main__":
            
    N = 100
    SNRs = [20, 5, 2, 0.5, -2, -5, -10, -20]
    
    for SNR in SNRs:
        drone_count = 0
        noise_count = 0
        for i in range(1, N+1):
            if i % (N // 10) == 0:
                print(f"Progress: {(i + 1) // (N // 10) * 10}%", end='\r', flush=True)
                
            dr_signal, dr_sr, dr_filename = load_audio("drone", SNR_db=SNR)
            dr_signal = scp_window_filter(dr_signal, sr=dr_sr, N=201, cutoff=[150, 2500], type="bandpass", window="hann")
            dr_main = main(dr_signal, dr_sr, dr_filename)
            if dr_main:
                drone_count += 1
                
            ns_signal, ns_sr, ns_filename = load_audio("noise", SNR_db = SNR)
            ns_signal = scp_window_filter(ns_signal, sr=ns_sr, N=201, cutoff=[150, 2500], type="bandpass", window="hann")
            ns_main = main(ns_signal, ns_sr, ns_filename)
            if not ns_main:
                noise_count += 1
        
        print()  # Clear the progress bar line
        drone_accuracy = 100 * (drone_count / N)
        noise_accuracy = 100 * (noise_count / N)
        print(f"At SNR_db: {SNR}")
        print(f"The accuracy for drone is {drone_accuracy:.2f}%")
        print(f"The accuracy for noise is {noise_accuracy:.2f}%\n")


