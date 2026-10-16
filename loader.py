from pathlib import Path

import pandas as pd
import wfdb
from scipy.signal import resample_poly

REF_FS = 500
WATCH_FS = 128
WINDOW_S = 30
TABLES = ["participants", "records", "watch_windows", "alignment", "data_dictionary"]


def load_tables(root):
    return {name: pd.read_csv(Path(root) / f"{name}.csv") for name in TABLES}


def record_path(root, record):
    return str(Path(root) / record.split("_")[0] / record)


def read_window(root, watch_record):
    return wfdb.rdrecord(record_path(root, watch_record)).p_signal[:, 0]


def read_segment(root, reference_record, leads=("I",), start=0, stop=None):
    record = wfdb.rdrecord(record_path(root, reference_record), channel_names=list(leads), sampfrom=start, sampto=stop)
    return record.p_signal


def read_reference(root, row, leads=("I",)):
    start = int(row.offset_sample_500hz)
    return read_segment(root, row.reference_record, leads, start, start + WINDOW_S * REF_FS)


def read_reference_128hz(root, row, leads=("I",)):
    start = int(row.offset_sample_500hz)
    x = read_segment(root, row.reference_record, leads, start - REF_FS, start + (WINDOW_S + 1) * REF_FS)
    return resample_poly(x, WATCH_FS, REF_FS, axis=0)[WATCH_FS:(WINDOW_S + 1) * WATCH_FS]


def select(alignment, reliable=True, core_set=False, condition=None):
    rows = alignment
    if reliable:
        rows = rows[rows.alignment_reliable]
    if core_set:
        rows = rows[rows.core_set]
    if condition:
        rows = rows[rows.condition == condition]
    return rows


def iter_pairs(root, rows, leads=("I",), at_128hz=True):
    read = read_reference_128hz if at_128hz else read_reference
    for row in rows.itertuples(index=False):
        yield row, read_window(root, row.watch_record), read(root, row, leads)
