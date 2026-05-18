import os
import shutil
import random
import numpy as np
import librosa as lb
from scipy.io import wavfile
from pathlib import Path
from filter import scp_window_filter
from spectrogram import main as generate_plots, add_noise

# Define folders
data_folder = "data"
unknown_folder = os.path.join(data_folder, "Binary_Drone_Audio", "unknown")
yes_drone_folder = os.path.join(data_folder, "Binary_Drone_Audio", "yes_drone")
temp_output = "temp_plots"
temp_audio = "temp_audio"

# Noise augmentation parameters
NOISE_FOLDER = unknown_folder  # Use unknown folder as noise source
#SNRs = [20,5,2,0.5,-2,-5,-10,-20]
SNRs = [20, 5, -5, -20]
#SNR_DB = -10  # Signal-to-Noise Ratio in dB (e.g., SNR_DB means signal power is SNR_DB x noise power)

for snr in SNRs:
    plots_folder = f"plots_SNR_{snr}"
    audio_folder = f"audio_SNR_{snr}"
    
    # Create output folders
    os.makedirs(plots_folder, exist_ok=True)
    os.makedirs(audio_folder, exist_ok=True)
    os.makedirs(temp_output, exist_ok=True)
    os.makedirs(temp_audio, exist_ok=True)

    # Get all files from both folders
    unknown_files = [f for f in os.listdir(unknown_folder) 
                    if os.path.isfile(os.path.join(unknown_folder, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]
    yes_drone_files = [f for f in os.listdir(yes_drone_folder) 
                    if os.path.isfile(os.path.join(yes_drone_folder, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]

    # Limit to 25 files each for 30 total (50-50 split)
    unknown_files = random.sample(unknown_files, min(25, len(unknown_files)))
    yes_drone_files = random.sample(yes_drone_files, min(25, len(yes_drone_files)))

    print(f"Using {len(unknown_files)} files from unknown (not) folder")
    print(f"Using {len(yes_drone_files)} files from yes_drone (yes) folder")
    print(f"Total files to process: {len(unknown_files) + len(yes_drone_files)}")

    # Create list with folder origin
    files_with_origin = []
    for f in unknown_files:
        files_with_origin.append((f, "not", unknown_folder))
    for f in yes_drone_files:
        files_with_origin.append((f, "yes", yes_drone_folder))

    # Shuffle randomly
    random.shuffle(files_with_origin)

    # ============================================================================
    # PLOTS GENERATION - Separate workflow
    # ============================================================================
    print(f"\n{'='*60}")
    print(f"Generating PLOTS (SNR {snr})")
    print(f"{'='*60}")
    
    plots_mapping = []
    for idx, (filename, origin_folder, source_folder) in enumerate(files_with_origin, 1):
        # Generate plots with noise augmentation
        generate_plots(source_folder, temp_output, filename, noise_folder=NOISE_FOLDER, snr_db=snr)
        
        # Move the generated plots to numbered folders
        temp_plot_dir = os.path.join(temp_output, filename)
        numbered_dir = os.path.join(plots_folder, str(idx))
        
        if os.path.exists(temp_plot_dir):
            shutil.move(temp_plot_dir, numbered_dir)
            print(f"✓ Plots folder {idx} created")
        else:
            print(f"✗ Warning: Plot directory not found for {filename}")
        
        # Record mapping
        plots_mapping.append(f"{idx}\t{origin_folder}\t{filename}")

    # Create plots mapping document
    plots_mapping_file = os.path.join(plots_folder, "mapping.txt")
    with open(plots_mapping_file, 'w') as f:
        f.write("Number\tLabel\tOriginal Filename\n")
        f.write("="*80 + "\n")
        for line in plots_mapping:
            f.write(line + "\n")

    # ============================================================================
    # AUDIO FILES GENERATION - Separate workflow
    # ============================================================================
    print(f"\n{'='*60}")
    print(f"Generating AUDIO FILES (SNR {snr})")
    print(f"{'='*60}")
    
    audio_mapping = []
    for idx, (filename, origin_folder, source_folder) in enumerate(files_with_origin, 1):
        # Load audio file
        src_audio_path = os.path.join(source_folder, filename)
        signal, sample_rate = lb.load(src_audio_path, sr=None, duration=1.0)
        
        # Add noise augmentation
        signal = add_noise(signal, sample_rate, NOISE_FOLDER, snr)
        signal = scp_window_filter(signal, sample_rate, N = 201, cutoff= [150, 2500], type = "bandpass")
        
        # Save augmented audio file with numbered filename
        file_ext = os.path.splitext(filename)[1]  # Get file extension
        dst_audio_path = os.path.join(audio_folder, f"{idx}{file_ext}")
        # Convert float signal to int16 for wav file
        signal_int16 = np.int16(signal * 32767)
        wavfile.write(dst_audio_path, int(sample_rate), signal_int16)
        print(f"✓ Audio file {idx}{file_ext} created")
        
        # Record mapping
        audio_mapping.append(f"{idx}{file_ext}\t{origin_folder}\t{filename}")

    # Create audio mapping document
    audio_mapping_file = os.path.join(audio_folder, "mapping.txt")
    with open(audio_mapping_file, 'w') as f:
        f.write("Number\tLabel\tOriginal Filename\n")
        f.write("="*80 + "\n")
        for line in audio_mapping:
            f.write(line + "\n")

    # Clean up temp folders
    for temp_folder in [temp_output, temp_audio]:
        if os.path.exists(temp_folder):
            try:
                shutil.rmtree(temp_folder)
            except PermissionError:
                print(f"Warning: Could not delete temp folder '{temp_folder}'. Files may be in use.")

    print(f"\n{'='*60}")
    print(f"✓ SNR {snr} processing complete!")
    print(f"✓ Plots saved to: {plots_folder}")
    print(f"  └─ Mapping: {plots_mapping_file}")
    print(f"✓ Audio files saved to: {audio_folder}")
    print(f"  └─ Mapping: {audio_mapping_file}")
    print(f"{'='*60}\n")
