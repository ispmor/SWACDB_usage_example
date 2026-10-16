# SWACDB usage example

Example code for the PhysioNet database *Simultaneous smartwatch and 12-lead electrocardiograms from healthy adults at rest before and after exercise*: 647 smartwatch lead I ECGs of 30 s (Garmin Venu 3), recorded during continuous 12-lead ECG from 32 healthy adults at rest before and after cycle-ergometer exercise, with a table aligning each window to its 12-lead segment.

The code reads the WFDB records and tables, pairs each smartwatch window with its time-matched reference lead I, and plots one pair or one 12-lead segment with its windows.

## Contents

- `loader.py`: reads the tables, a window, a 12-lead segment and the time-matched reference of a window (at 500 Hz, or resampled to 128 Hz)
- `examples/plot_pair.py`: one window over its time-matched reference lead I
- `examples/plot_segment.py`: one 12-lead segment with the position and alignment status of its windows
- `examples/style.py`: plot style shared by the examples

## Setup

Python 3.10 or newer.

```bash
pip install -r requirements.txt
```

Download the database from PhysioNet (link to be added) and point `--data` at the folder that contains `RECORDS`:

```bash
wget -r -N -c -np https://physionet.org/files/<project-slug>/1.0.0/
```

## Quick start

```python
from loader import iter_pairs, load_tables, select

tables = load_tables("path/to/database")
rows = select(tables["alignment"], reliable=True, core_set=True)
for row, watch, reference in iter_pairs("path/to/database", rows):
    print(row.watch_record, watch.shape, reference.shape)
```

`watch` is the smartwatch lead I in mV at 128 Hz (3,840 samples). `reference` is the time-matched reference lead I in mV, anti-alias filtered and resampled to 128 Hz (3,840 × 1). Use `at_128hz=False` for the reference at 500 Hz (15,000 samples) and `leads=[...]` for other leads.

## Examples

```bash
python examples/plot_pair.py --data path/to/database --window P01_watch_02_pre_exercise --out figures/pair.png
python examples/plot_segment.py --data path/to/database --segment P01_rest_post_exercise --out figures/segment.png
```

Without `--out`, the figure opens in a window.

## Using the data

- Pair windows with 12-lead segments through `alignment.csv`, not through the header start times: the device clocks were not synchronised.
- Use windows with `alignment_reliable` True for beat-by-beat comparison. Windows with `align_method` `clock_median_latency` carry clock-based offsets and are not suitable for it.
- Compare the two signals in the band they share: the watch export is limited to 128 Hz.
- The rhythm classifications and heart rates in `watch_windows.csv` are unmodified outputs of the watch app, not clinical labels.
- Windows of one participant are not independent; split training and test sets by participant.

The Usage Notes on the PhysioNet project page give the details.

## Citation

If you use the data, cite the PhysioNet project (DOI to be added). If you use this code, cite it as given in `CITATION.cff`.

## Licence

The code is released under the MIT licence (`LICENSE`). The data are not part of this repository; PhysioNet distributes them under CC BY-SA 4.0.
