import os
import numpy as np
import librosa as lb
import matplotlib.pyplot as plt


def main(subdir: str, output_folder: str, filename: str) -> None:
    """
    Plots the time vs amplitude of an audio signal,
    and computes the spectrogram of the signal

    Args:
        subdir (str): the directory from which to fetch the audio signal
        filename (str): The name of the file

    Returns:
        None: The two plots, in a subfolder of an output folder
    """
    
    #Making the output folder
    outputdir = os.path.join(output_folder, filename)
    os.makedirs(outputdir, exist_ok=True)
    
    #Finds the signal and loads it
    path = os.path.join(subdir, filename)
    signal, sample_rate = lb.load(path, sr= None, duration = 1.0)
    """ path2 = os.path.join("data","støvsuger.wav")
    signal2, sample_rate2 = lb.load(path2, sr = 16_000, duration = 1.0)
    signal2 = signal2[:len(signal)] * 0.1
    signal = signal[:len(signal2)]
    signal += signal2
    signal = signal *0.5 """

    #Plots amplitude vs time
    lb.display.waveshow(signal, sr=sample_rate)
    plt.ylabel("Relative amplitude")
    plt.xlabel("Time [s]")
    outputpath = os.path.join(outputdir,  "time plot")
    plt.savefig(outputpath)
    plt.clf()

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
    plt.clf()


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
            
        
        
                
        
        
