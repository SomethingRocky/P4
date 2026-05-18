import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d.axes3d import Axes3D
from typing import cast
import librosa
import plotly.graph_objects as go

# Source - https://stackoverflow.com/a/49719413
# Posted by OriolAbril, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-13, License - CC BY-SA 3.0

def waterfall_plot(fig, ax: Axes3D, X, Y, Z):
    '''
    Make a waterfall plot
    Input:
        fig,ax : matplotlib figure and axes to populate
        Z : n,m numpy array. Must be a 2d array even if only one line should be plotted
        X,Y : n,m array
    '''
    # Set normalization to the same values for all lines.
    norm = Normalize(Z.min().min(), Z.max().max())

    # Check sizes to loop always over the smallest dimension.
    n,m = Z.shape
    if n>m:
        X=X.T; Y=Y.T; Z=Z.T
        m,n = n,m

    for j in range(n):
        # Build line segments for this time slice.
        points = np.array([X[j,:], Z[j,:]]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)        
        segment_list = [np.asarray(seg) for seg in segments]
        lc = LineCollection(segment_list, cmap='plasma', norm=norm)
        # Use midpoint amplitude to color each segment.
        lc.set_array((Z[j,1:]+Z[j,:-1])/2)
        lc.set_linewidth(2)
        ax.add_collection3d(lc,zs=(Y[j,1:]+Y[j,:-1])/2, zdir='y')

    # Add one shared colorbar.
    fig.colorbar(lc, ax=ax, pad=0.1, label='Amplitude (dB)')
    

# Trumpet waterfall: frequency over time over amplitude.
audio, sampling_rate = librosa.load(librosa.ex("trumpet"), sr=None)
n_fft = 1024
hop_length = 128

D = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length, window="hann")
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

frequency = librosa.fft_frequencies(sr=sampling_rate, n_fft=n_fft)
time = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sampling_rate, hop_length=hop_length, n_fft=n_fft)

X, Y = np.meshgrid(frequency, time)
Z = S_db.T

fig = plt.figure()
ax = cast(Axes3D, fig.add_subplot(111, projection='3d'))
waterfall_plot(fig, ax, X, Y, Z)

ax.set_xlabel('Frequency (Hz)')
ax.set_xlim3d(0, sampling_rate / 2)
ax.set_ylabel('Time (s)')
ax.set_ylim3d(time.min(), time.max())
ax.set_zlabel('Amplitude (dB)')
ax.set_zlim3d(np.min(Z), np.max(Z))
ax.view_init(elev=30, azim=-60)

plt.tight_layout()

# Save to file (PNG)
fig.savefig("trumpet_waterfall.png", dpi=300, bbox_inches="tight")

# Interactive plot
fig_p = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale="Plasma")])
fig_p.update_layout(
    scene=dict(
        xaxis_title="Frequency (Hz)",
        yaxis_title="Time (s)",
        zaxis_title="Amplitude (dB)"
    )
)
fig_p.write_html("trumpet_waterfall_interactive.html")