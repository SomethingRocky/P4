import numpy as np
import librosa as lb
import plotly.graph_objects as go


def create_demo_signal(sample_freq: float = 24e3, signal_length: float = 30):
	sample_time = 1 / sample_freq
	samples = int(signal_length / sample_time)

	t = np.array([i * sample_time for i in range(samples)])
	signal = np.sin(1000 * t**2)

	u = np.zeros_like(t)
	u[: samples // 2] = t[: samples // 2]
	signal += np.sin(2 * np.pi * 2000 * u)

	return t, signal


def compute_spectrogram(signal, sample_freq, window="hann", window_length=256, hop_length=None):
	if hop_length is None:
		hop_length = window_length // 2

	stft = lb.stft(signal, window=window, n_fft=window_length, hop_length=hop_length)
	stft_db = lb.amplitude_to_db(np.abs(stft), ref=np.max, top_db=120)
	frequency = lb.fft_frequencies(sr=sample_freq, n_fft=window_length)
	time = lb.frames_to_time(np.arange(stft_db.shape[1]), sr=sample_freq, hop_length=hop_length, n_fft=window_length)

	return frequency, time, stft_db
if __name__ == "__main__":
	sample_freq = 24e3
	_, signal = create_demo_signal(sample_freq=sample_freq)
	frequency, time, stft_db = compute_spectrogram(signal, sample_freq, window="hann", window_length=128)

	X, Y = np.meshgrid(frequency, time)
	Z = stft_db.T

	plot_step_time = max(1, Y.shape[0] // 200)
	plot_step_freq = max(1, X.shape[1] // 200)
	fig_p = go.Figure(data=[go.Surface(x=X[::plot_step_time, ::plot_step_freq], y=Y[::plot_step_time, ::plot_step_freq], z=Z[::plot_step_time, ::plot_step_freq], colorscale="Inferno")])
	fig_p.update_layout(
		scene=dict(
			xaxis_title="Frequency (Hz)",
			yaxis_title="Time (s)",
			zaxis_title="Amplitude (dB)",
		)
	)
	fig_p.write_html("waterfall_spectrogram_interactive.html")
