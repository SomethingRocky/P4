
import argparse
import os
from pathlib import Path
import random

import librosa as lb
import numpy as np
import scipy.io.wavfile as wav








# Define folders
data_folder = "data"
unknown_folder = os.path.join(data_folder, "Binary_Drone_Audio", "unknown")
yes_drone_folder = os.path.join(data_folder, "Binary_Drone_Audio", "yes_drone")
output_folder = "combined_wav_-10"


# Noise augmentation parameters
NOISE_FOLDER = unknown_folder  # Use unknown folder as noise source
SNR_DB = -10  # Signal-to-Noise Ratio in dB (e.g., SNR_DB means signal power is SNR_DB x noise power)


# Create output folders
os.makedirs(output_folder, exist_ok=True)


# Get all files from both folders
unknown_files = [f for f in os.listdir(unknown_folder) 
                 if os.path.isfile(os.path.join(unknown_folder, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]
yes_drone_files = [f for f in os.listdir(yes_drone_folder) 
                   if os.path.isfile(os.path.join(yes_drone_folder, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]


# Limit to 15 files each for 30 total (50-50 split)
unknown_files = random.sample(unknown_files, min(15, len(unknown_files)))
yes_drone_files = random.sample(yes_drone_files, min(15, len(yes_drone_files)))

print(f"Using {len(unknown_files)} files from unknown (not) folder")
print(f"Using {len(yes_drone_files)} files from yes_drone (yes) folder")
print(f"Total folders to create: {len(unknown_files) + len(yes_drone_files)}")


Files_with_origin = []
for f in unknown_files:
    Files_with_origin.append((f, "not", unknown_folder))
for f in yes_drone_files:
    Files_with_origin.append((f, "yes", yes_drone_folder))
    
random.shuffle(Files_with_origin)




# Generate plots and create mapping
mapping = []
for idx, (filename, origin_folder, source_folder) in enumerate(Files_with_origin, 1):

    # Load the signal
    path = os.path.join(source_folder, filename)
    signal, sample_rate = lb.load(path, sr=None, duration=1.0)
    
    # Add noise augmentation if noise folder is provided
    if NOISE_FOLDER is not None and SNR_DB is not None and os.path.exists(NOISE_FOLDER):
        noise_files = [f for f in os.listdir(NOISE_FOLDER) 
                      if os.path.isfile(os.path.join(NOISE_FOLDER, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]
        if noise_files:
            # Select random noise file
            random_noise_file = random.choice(noise_files)
            noise_path = os.path.join(NOISE_FOLDER, random_noise_file)
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
                snr_linear = 10 ** (SNR_DB / 10)
                
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
    
    # Save the mixed signal as WAV
    output_wav_path = os.path.join(output_folder, f"{idx}.wav")
    wav.write(output_wav_path, sample_rate, (signal * 32767).astype(np.int16))  # Convert to 16-bit PCM
    
    print(f"Created WAV file {idx}.wav from {origin_folder}/{filename}")
    
    # Record mapping
    mapping.append(f"{idx}\t{origin_folder}\t{filename}")

# Create mapping document
mapping_file = os.path.join(output_folder, "mapping.txt")
with open(mapping_file, 'w') as f:
    f.write("Number\tFolder\tOriginal Filename\n")
    f.write("="*80 + "\n")
    for line in mapping:
        f.write(line + "\n")

print(f"\n✓ All spectrograms generated and organized!")
print(f"✓ Plots saved to: {output_folder}")
print(f"✓ Mapping saved to: {mapping_file}")