""" Data: compute SSD filters for all subjects and save them.
"""
import pandas as pd
import mne
import numpy as np
import os

import ssd
from helper import print_progress
from params import EEG_DATA_FOLDER, SSD_BANDWIDTH, SNR_THRESHOLD, SSD_EEG_DIR, SPEC_PARAM_CSV_EEG

# %% specify participants and folders
df = pd.read_csv(SPEC_PARAM_CSV_EEG)
df = df[df.peak_amplitude > SNR_THRESHOLD]
df = df.set_index("subject")
subjects = df.index

os.makedirs(SSD_EEG_DIR, exist_ok=True)
conditions = ("eo", "ec")

# %% compute for all participants
for i_sub, subject in enumerate(subjects):
    print_progress(i_sub, subject, subjects)

    for i_cond, condition in enumerate(conditions):

        ssd_file_name = f"{SSD_EEG_DIR}/{subject}_ssd_{condition}.npy"

        if os.path.exists(ssd_file_name):
            continue

        # load data
        file_name = f"{EEG_DATA_FOLDER}/{subject}_{condition}-raw.fif"
        raw = mne.io.read_raw_fif(file_name)
        raw.load_data()
        raw.pick_types(eeg=True)
        raw.set_eeg_reference("average")

        # compute SSD in narrow band
        peak = df.loc[subject]["peak_frequency"]
        signal_bp = [peak - SSD_BANDWIDTH, peak + SSD_BANDWIDTH]
        noise_bp = [peak - (SSD_BANDWIDTH + 2), peak + (SSD_BANDWIDTH + 2)]
        noise_bs = [peak - (SSD_BANDWIDTH + 1), peak + (SSD_BANDWIDTH + 1)]
        filters, patterns = ssd.compute_ssd(raw, signal_bp, noise_bp, noise_bs)

        # save patterns and filters
        results = dict(filters=filters, patterns=patterns, peak=peak)
        np.save(ssd_file_name, results)
