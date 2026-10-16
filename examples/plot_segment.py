import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loader import REF_FS, WINDOW_S, load_tables, read_segment
from style import INK_2, MARKERS, STATUS, SURFACE


def status(row):
    if row.alignment_reliable:
        return "reliable"
    if row.align_method == "clock_median_latency":
        return "unreliable, clock-based offset"
    return "unreliable, signal-derived offset"


parser = argparse.ArgumentParser()
parser.add_argument("--data", required=True)
parser.add_argument("--segment", default="P01_rest_post_exercise")
parser.add_argument("--lead", default="I")
parser.add_argument("--out")
args = parser.parse_args()

alignment = load_tables(args.data)["alignment"]
windows = alignment[alignment.reference_record == args.segment]
signal = read_segment(args.data, args.segment, [args.lead])[:, 0]
t = np.arange(signal.size) / REF_FS

fig, (lane, ax) = plt.subplots(2, 1, figsize=(12, 4.8), sharex=True, height_ratios=[1, 4], constrained_layout=True)
ax.plot(t, signal, color=INK_2, lw=0.4)
for row in windows.itertuples():
    kind = status(row)
    centre = row.offset_s + WINDOW_S / 2
    ax.axvspan(row.offset_s, row.offset_s + WINDOW_S, color=STATUS[kind], alpha=0.12, lw=0)
    lane.hlines(0, row.offset_s, row.offset_s + WINDOW_S, color=STATUS[kind], lw=6)
    lane.plot(centre, 0, MARKERS[kind], color=STATUS[kind], ms=8, mec=SURFACE, mew=2)
    lane.text(centre, 0.5, f"{row.order_in_condition:02d}", ha="center", va="bottom", color=INK_2)

lane.set_title(f"{args.segment}, lead {args.lead}, with its {len(windows)} smartwatch windows")
lane.set_ylim(-1, 1.6)
lane.axis("off")
handles = [Line2D([], [], marker=MARKERS[k], color=STATUS[k], ls="", ms=8, label=k) for k in STATUS]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncols=3)
ax.set_xlabel("Time from segment start (s)")
ax.set_ylabel("mV")
ax.set_xlim(0, t[-1])

if args.out:
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
else:
    plt.show()
