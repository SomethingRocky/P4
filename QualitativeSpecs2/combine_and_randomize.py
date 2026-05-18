import os
import shutil
import random
from pathlib import Path
from spectrogram_test import main as generate_plots

# Define folders
data_folder = "data"
not_folder = os.path.join(data_folder, "not")
yes_folder = os.path.join(data_folder, "yes")
output_folder = "combined"
temp_output = "temp_plots"

# Create output folders
os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_output, exist_ok=True)

# Get all files from both folders
not_files = [f for f in os.listdir(not_folder) if os.path.isfile(os.path.join(not_folder, f))]
yes_files = [f for f in os.listdir(yes_folder) if os.path.isfile(os.path.join(yes_folder, f))]

# Create list with folder origin
files_with_origin = []
for f in not_files:
    files_with_origin.append((f, "not"))
for f in yes_files:
    files_with_origin.append((f, "yes"))

# Shuffle randomly
random.shuffle(files_with_origin)

# Generate plots and create mapping
mapping = []
for idx, (filename, origin_folder) in enumerate(files_with_origin, 1):
    # Determine source folder
    if origin_folder == "not":
        source_folder = not_folder
    else:
        source_folder = yes_folder
    
    # Generate plots
    generate_plots(source_folder, temp_output, filename)
    
    # Move the generated plots to numbered folders
    temp_plot_dir = os.path.join(temp_output, filename)
    numbered_dir = os.path.join(output_folder, str(idx))
    
    if os.path.exists(temp_plot_dir):
        shutil.move(temp_plot_dir, numbered_dir)
        print(f"Created folder {idx} with plots from {origin_folder}/{filename}")
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
    shutil.rmtree(temp_output)

print(f"\n✓ All spectrograms generated and organized!")
print(f"✓ Plots saved to: {output_folder}")
print(f"✓ Mapping saved to: {mapping_file}")
