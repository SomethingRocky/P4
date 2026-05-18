import os
import numpy as np
import librosa as lb
import matplotlib.pyplot as plt
import random


def main(subdir: str, output_folder: str, filename: str, noise_folder: str = None, snr_db: float = None) -> None:
    """
    Plots the time vs amplitude of an audio signal,
    and computes the spectrogram of the signal

    Args:
        subdir (str): the directory from which to fetch the audio signal
        output_folder (str): The folder where output plots are saved
        filename (str): The name of the file
        noise_folder (str): Optional folder to load random noise from
        snr_db (float): Signal-to-Noise Ratio in dB (e.g., 10 for 10dB SNR). If None, no noise is added.

    Returns:
        None: The two plots, in a subfolder of an output folder
    """
    
    #Making the output folder
    outputdir = os.path.join(output_folder, filename)
    os.makedirs(outputdir, exist_ok=True)
    
    #Finds the signal and loads it
    path = os.path.join(subdir, filename)
    signal, sample_rate = lb.load(path, sr= None, duration = 1.0)
    
    # Add noise augmentation if noise folder is provided
    if noise_folder is not None and snr_db is not None and os.path.exists(noise_folder):
        noise_files = [f for f in os.listdir(noise_folder) 
                      if os.path.isfile(os.path.join(noise_folder, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]
        if noise_files:
            # Select random noise file
            random_noise_file = random.choice(noise_files)
            noise_path = os.path.join(noise_folder, random_noise_file)
            noise, noise_sr = lb.load(noise_path, sr=sample_rate, duration=1.0)
            
            # Match noise length to signal
            if len(noise) < len(signal):
                noise = np.pad(noise, (0, len(signal) - len(noise)), mode='wrap')
            else:
                noise = noise[:len(signal)]
            
            # Calculate signal and noise power
            signal_power = np.mean(signal ** 2)
            noise_power = np.mean(noise ** 2)
            
            # Only add noise if both signal and noise have valid power
            if signal_power > 0 and noise_power > 0:
                # Convert SNR from dB to linear
                snr_linear = 10 ** (snr_db / 10)
                
                # Calculate scaling factor for noise
                noise_scale = np.sqrt(signal_power / (snr_linear * noise_power + 1e-10))
                
                # Mix signal with scaled noise
                signal = signal + noise_scale * noise
                
                # Normalize to prevent clipping
                max_val = np.max(np.abs(signal))
                if max_val > 0 and max_val < np.inf:
                    signal = signal / max_val
                
                # Ensure no NaN or inf values
                signal = np.nan_to_num(signal, nan=0.0, posinf=1.0, neginf=-1.0)
    

    #Plots amplitude vs time
    lb.display.waveshow(signal, sr=sample_rate)
    plt.ylabel("Relative amplitude")
    plt.xlabel("Time [s]")
    outputpath = os.path.join(outputdir,  "time plot")
    plt.savefig(outputpath)
    plt.close('all')

    #Computes and plots frequency vs time
    stft = lb.stft(signal)
    stft_db = lb.amplitude_to_db(np.abs(stft) ** 2, ref = np.max, top_db= 80)
    lb.display.specshow(stft_db, sr=sample_rate, x_axis="time", y_axis="hz")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [s]")
    plt.colorbar(label = "Power [dBFS]")
    outputpath = os.path.join(outputdir, "freq plot")
    plt.savefig(outputpath)
    plt.ylim(0,2000)
    plt.savefig(outputpath + "zoomed")
    plt.close('all')


if __name__ == "__main__":
    for dir, folders, files in os.walk("data"):
        if len(files) != 0:
            for file in files:
                if dir == "data":
                    """
                    if there are files in the data folder,
                    they should not go straight in the output folder,
                    hence they go in a "data" folder in output instead
                    """
                    outputpath = os.path.join("output", "data")
                else: 
                    path = os.path.relpath(dir, "data") #Removing data prefix
                    outputpath = os.path.join("output", path)
                main(dir, outputpath, file)
            
        
        
                
        
        
