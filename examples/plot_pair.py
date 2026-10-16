import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loader import REF_FS, WATCH_FS, load_tables, read_reference, read_reference_128hz, read_window
from style import BLUE, ORANGE


def normalise(x):
    x = sosfiltfilt(butter(4, [0.5, 40], btype="bandpass", fs=WATCH_FS, output="sos"), x)
    return (x - x.mean()) / x.std()


parser = argparse.ArgumentParser()
parser.add_argument("--data", required=True)
parser.add_argument("--window", default="P01_watch_02_pre_exercise")
parser.add_argument("--out")
args = parser.parse_args()

tables = load_tables(args.data)
row = tables["alignment"].set_index("watch_record").loc[args.window]
app = tables["watch_windows"].set_index("watch_record").loc[args.window]

watch = read_window(args.data, args.window)
reference = read_reference(args.data, row)[:, 0]
reference_128 = read_reference_128hz(args.data, row)[:, 0]
t = np.arange(watch.size) / WATCH_FS
zoom = (t >= 10) & (t < 15)

fig, axes = plt.subplots(3, 1, figsize=(11, 7.5), constrained_layout=True)
axes[0].sharex(axes[1])
axes[0].plot(t, watch, color=BLUE, lw=1)
axes[0].set_title("Smartwatch lead I, 128 Hz")
axes[1].plot(np.arange(reference.size) / REF_FS, reference, color=ORANGE, lw=1)
axes[1].set_title(f"Reference lead I, 500 Hz: {row.reference_record} from {row.offset_s:.3f} s")
axes[2].plot(t[zoom], normalise(reference_128)[zoom], color=ORANGE, lw=1.5, label="Reference lead I, resampled to 128 Hz")
axes[2].plot(t[zoom], normalise(watch)[zoom], color=BLUE, lw=1.5, label="Smartwatch lead I")
axes[2].set_title("10-15 s, both at 128 Hz, 0.5-40 Hz band-pass, z-scored")
axes[2].legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncols=2)
axes[0].set_ylabel("mV")
axes[1].set_ylabel("mV")
axes[2].set_ylabel("z-score")
axes[1].set_xlabel("Time from window start (s)")
axes[2].set_xlabel("Time from window start (s)")
fig.suptitle(
    f"{args.window}\nalignment_reliable {row.alignment_reliable}, {row.align_method}, beat_jitter_ratio {row.beat_jitter_ratio}"
    f"; watch app: {app.device_rhythm_classification}, {app.device_heart_rate_bpm} bpm",
    x=0.01, ha="left", fontsize=10,
)

if args.out:
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
else:
    plt.show()
