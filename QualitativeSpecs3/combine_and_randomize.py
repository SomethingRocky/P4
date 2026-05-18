import os
import shutil
import random
from pathlib import Path
from spectrogram_test import main as generate_plots

# Define folders
data_folder = "data"
unknown_folder = os.path.join(data_folder, "Binary_Drone_Audio", "unknown")
yes_drone_folder = os.path.join(data_folder, "Binary_Drone_Audio", "yes_drone")
output_folder = "combinedtester4"
temp_output = "temp_plots"

# Noise augmentation parameters
NOISE_FOLDER = unknown_folder  # Use unknown folder as noise source
SNR_DB = 2  # Signal-to-Noise Ratio in dB (e.g., SNR_DB means signal power is SNR_DB x noise power)

# Create output folders
os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_output, exist_ok=True)

# Get all files from both folders
unknown_files = [f for f in os.listdir(unknown_folder) 
                 if os.path.isfile(os.path.join(unknown_folder, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]
yes_drone_files = [f for f in os.listdir(yes_drone_folder) 
                   if os.path.isfile(os.path.join(yes_drone_folder, f)) and f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]

# Limit to 25 files each for 50 total (50-50 split)
unknown_files = random.sample(unknown_files, min(25, len(unknown_files)))
yes_drone_files = random.sample(yes_drone_files, min(25, len(yes_drone_files)))

print(f"Using {len(unknown_files)} files from unknown (not) folder")
print(f"Using {len(yes_drone_files)} files from yes_drone (yes) folder")
print(f"Total folders to create: {len(unknown_files) + len(yes_drone_files)}")

# Create list with folder origin
files_with_origin = []
for f in unknown_files:
    files_with_origin.append((f, "not", unknown_folder))
for f in yes_drone_files:
    files_with_origin.append((f, "yes", yes_drone_folder))

# Shuffle randomly
random.shuffle(files_with_origin)

# Generate plots and create mapping
mapping = []
for idx, (filename, origin_folder, source_folder) in enumerate(files_with_origin, 1):
    # Generate plots with noise augmentation
    generate_plots(source_folder, temp_output, filename, noise_folder=NOISE_FOLDER, snr_db=SNR_DB)
    
    # Move the generated plots to numbered folders
    temp_plot_dir = os.path.join(temp_output, filename)
    numbered_dir = os.path.join(output_folder, str(idx))
    
    if os.path.exists(temp_plot_dir):
        shutil.move(temp_plot_dir, numbered_dir)
        print(f"Created folder {idx}") #with plots from {origin_folder}/{filename}
    else:
        print(f"Warning: Plot directory not found for {filename}")
    
    # Record mapping
    mapping.append(f"{idx}\t{origin_folder}\t{filename}")

# Create mapping document
mapping_file = os.path.join(output_folder, "mapping.txt")
with open(mapping_file, 'w') as f:
    f.write("Number\tFolder\tOriginal Filename\n")
    f.write("="*80 + "\n")
    for line in mapping:
        f.write(line + "\n")

# Clean up temp folder
if os.path.exists(temp_output):
    try:
        shutil.rmtree(temp_output)
    except PermissionError:
        print(f"Warning: Could not delete temp folder '{temp_output}'. Files may be in use.")
        print(f"You can manually delete it later.")

print(f"\n✓ All spectrograms generated and organized!")
print(f"✓ Plots saved to: {output_folder}")
print(f"✓ Mapping saved to: {mapping_file}")
