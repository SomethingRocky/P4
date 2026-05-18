import argparse
import os
from pathlib import Path

import librosa as lb
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav


# 5, 2, 0.5, -2, -5, -20

SNR_DB = 800 # Signal-to-Noise Ratio in dB for mixing file2 into file1


def load_audio(path: str, duration: float | None = 1.0, sr: int | None = None) -> tuple[np.ndarray, int]:
    """Load an audio file with librosa."""
    signal, sample_rate = lb.load(path, sr=sr, duration=duration)
    return signal, sample_rate


def scale_noise_for_snr(signal: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    """Scale noise to achieve desired SNR relative to the signal."""
    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)
    if noise_power == 0:
        return noise

    target_noise_power = signal_power / (10 ** (snr_db / 10))
    scaling = np.sqrt(target_noise_power / noise_power)
    return noise * scaling


def mix_signals(signal_a: np.ndarray, signal_b: np.ndarray, snr_db: float | None = None) -> np.ndarray:
    """Mix two signals by averaging or by scaling the second signal to a target SNR."""
    max_len = max(len(signal_a), len(signal_b))
    a = np.pad(signal_a, (0, max_len - len(signal_a)), mode="constant")
    b = np.pad(signal_b, (0, max_len - len(signal_b)), mode="constant")

    if snr_db is not None:
        b = scale_noise_for_snr(a, b, snr_db)
        mixed = a + b
    else:
        mixed = (a + b) / 2.0

    max_amp = np.max(np.abs(mixed))
    if max_amp > 0:
        mixed = mixed / max_amp
    return mixed


def save_spectrogram_plots(signal: np.ndarray, sample_rate: int, output_dir: str, basename: str = "combined") -> None:
    """Save time-domain and spectrogram plots for a signal."""
    os.makedirs(output_dir, exist_ok=True)

    # Time-domain plot
    plt.figure()
    lb.display.waveshow(signal, sr=sample_rate)
    plt.ylabel("Relative amplitude")
    plt.xlabel("Time [s]")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{basename}_time.png"))
    plt.clf()

    # Spectrogram plot
    stft = lb.stft(signal)
    stft_db = lb.amplitude_to_db(np.abs(stft) ** 2, ref=np.max, top_db=80)
    plt.figure()
    lb.display.specshow(stft_db, sr=sample_rate, x_axis="time", y_axis="hz")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [s]")
    plt.colorbar(label="Power [dBFS]")
    plt.ylim(0, 2500)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{basename}_spectrogram.png"))
    plt.clf()


def main(file1: str, file2: str, output_folder: str, duration: float | None = 1.0, snr_db: float | None = None) -> None:
    """Combine two audio files and generate spectrogram plots."""
    file1_path = Path("C:\\Users\\Leo\\OneDrive - Aalborg Universitet\\Mathias Fischer Kjærs filer - P4\\Koder\\Hør_en_drone_eksperiment\\data\\Binary_Drone_Audio\\yes_drone\\B_S2_D1_082-bebop_003_.wav")
    file2_path = Path("C:\\Users\\Leo\\OneDrive - Aalborg Universitet\\Mathias Fischer Kjærs filer - P4\\Koder\\Hør_en_drone_eksperiment\\data\\støvsuger.wav")
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    signal_a, sr_a = load_audio(str(file1_path), duration=duration)
    signal_b, sr_b = load_audio(str(file2_path), duration=duration)

    if sr_a != sr_b:
        if sr_a > sr_b:
            signal_b = lb.resample(signal_b, orig_sr=sr_b, target_sr=sr_a)
            sr_b = sr_a
        else:
            signal_a = lb.resample(signal_a, orig_sr=sr_a, target_sr=sr_b)
            sr_a = sr_b

    mixed_signal = mix_signals(signal_a, signal_b, snr_db=snr_db)
    save_spectrogram_plots(mixed_signal, sr_a, str(output_path), basename="combined")

    combined_audio_path = output_path / "combined_audio.wav"
    wav.write(str(combined_audio_path), sr_a, mixed_signal.astype(np.float32))
    print(f"Saved combined spectrogram plots to: {output_path}")
    print(f"Saved combined audio to: {combined_audio_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine two audio files and generate spectrogram plots.")
    parser.add_argument("file1", nargs='?', default="b_s2_d1_109-bebop_003_.wav", help="Path to the first audio file")
    parser.add_argument("file2", nargs='?', default="støvsuger.wav", help="Path to the second audio file")
    parser.add_argument("--output", default="combined_spec_output", help="Output folder for plots and combined audio")
    parser.add_argument("--duration", type=float, default=1.0, help="Duration in seconds to load from each file")
    parser.add_argument("--snr-db", type=float, default=SNR_DB, help="Signal-to-noise ratio in dB for mixing file2 into file1")
    args = parser.parse_args()

    main(args.file1, args.file2, args.output, duration=args.duration, snr_db=args.snr_db)



