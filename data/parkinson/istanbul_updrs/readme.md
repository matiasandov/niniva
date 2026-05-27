Here's a full breakdown of all 29 columns, mapped to your sample row:

# Instances 1040

20 PWP (6 female, 14 male) and 20 healthy individuals (10 female, 10 male) who appealed at the Department of Neurology in Cerrahpasa Faculty of Medicine, Istanbul University. From all subjects, multiple types of sound recordings

---

**Sample row:**
`1, 0.728, 0.000037698, 0.353, 0.376, 1.059, 5.864, 0.642, 2.058, 3.18, 7.194, 6.175, 0.951285, 0.066758, 17.403, 195.252, 193.289, 14.773, 159.515, 234.505, 170, 169, 0.005181253, 0.000403494, 2.247, 0, 0, 23, 1`

---

### Col 1 — Subject ID
`1` — The identifier for the subject (patient or healthy person).

---

### Cols 2–6 — Jitter (vocal frequency variation)
Jitter measures how much the pitch/frequency varies from cycle to cycle. Higher jitter = less stable voice, common in Parkinson's.

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 2 | Jitter (local) | 0.728 | Cycle-to-cycle variation as a % of period |
| 3 | Jitter (local, absolute) | 0.0000377 | Same but in seconds (absolute time) |
| 4 | Jitter (RAP) | 0.353 | Relative Average Perturbation — avg over 3 cycles |
| 5 | Jitter (PPQ5) | 0.376 | 5-point Period Perturbation Quotient |
| 6 | Jitter (DDP) | 1.059 | Average absolute diff between consecutive differences (= RAP × 3) |

---

### Cols 7–12 — Shimmer (vocal amplitude variation)
Shimmer measures how much the loudness/amplitude varies. Higher shimmer = irregular amplitude, also a Parkinson's indicator.

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 7 | Shimmer (local) | 5.864 | Cycle-to-cycle amplitude variation (%) |
| 8 | Shimmer (local, dB) | 0.642 | Same but in decibels |
| 9 | Shimmer (APQ3) | 2.058 | 3-point Amplitude Perturbation Quotient |
| 10 | Shimmer (APQ5) | 3.18 | 5-point Amplitude Perturbation Quotient |
| 11 | Shimmer (APQ11) | 7.194 | 11-point Amplitude Perturbation Quotient |
| 12 | Shimmer (DDA) | 6.175 | Avg absolute diff between consecutive amplitude differences (= APQ3 × 3) |

---

### Cols 13–15 — Harmonics / Noise Ratios
These measure the ratio of harmonic (tonal) signal to noise in the voice.

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 13 | AC (Autocorrelation) | 0.951285 | Degree of periodicity in the signal (0–1, higher = more regular) |
| 14 | NTH (Noise-to-Harmonics) | 0.066758 | Noise relative to harmonics — higher = noisier voice |
| 15 | HTN (Harmonics-to-Noise) | 17.403 | Inverse of NTH — higher = cleaner, more harmonic voice |

---

### Cols 16–20 — Pitch Statistics (in Hz)

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 16 | Median pitch | 195.252 Hz | Middle pitch value across the recording |
| 17 | Mean pitch | 193.289 Hz | Average pitch |
| 18 | Std deviation of pitch | 14.773 Hz | How much pitch fluctuates |
| 19 | Minimum pitch | 159.515 Hz | Lowest pitch detected |
| 20 | Maximum pitch | 234.505 Hz | Highest pitch detected |

---

### Cols 21–24 — Pulse / Period Statistics

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 21 | Number of pulses | 170 | Total glottal pulses counted in the recording |
| 22 | Number of periods | 169 | Total vocal periods (one less than pulses) |
| 23 | Mean period | 0.005181 s | Average duration of one vocal cycle (~5.2 ms) |
| 24 | Std deviation of period | 0.000403 s | Variability in period duration |

---

### Cols 25–27 — Voicing / Voice Break Features

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 25 | Fraction of locally unvoiced frames | 2.247 | % of frames where voice drops out |
| 26 | Number of voice breaks | 0 | Count of complete voice interruptions |
| 27 | Degree of voice breaks | 0 | Total duration of breaks as % of signal |

---

### Col 28 — UPDRS Score
`23` — The **Unified Parkinson's Disease Rating Scale** score, assigned by a physician. Only present for PD patients (0 for healthy subjects). Higher = more severe symptoms. Used for **regression** tasks.

### Col 29 — Class Label
`1` — The target for **classification**: `1` = Parkinson's patient, `0` = healthy subject.

---

**In summary**, the features capture three main dimensions of voice quality: pitch stability (jitter), amplitude stability (shimmer), and noise/harmonic structure — all of which degrade measurably with Parkinson's disease.

Scaled features with StandardScaler:

acoustic_features = [
    'jitter_local', 'jitter_local_abs', 'jitter_rap',
       'jitter_ppq5', 'jitter_ddp', 'shimmer_local', 'shimmer_local_db',
       'shimmer_apq3', 'shimmer_apq5', 'shimmer_apq11', 'shimmer_dda', 'ac',
       'nth', 'htn', 'pitch_median', 'pitch_mean', 'pitch_std', 'pitch_min',
       'pitch_max', 'num_pulses', 'mean_period', 'std_period',
       'unvoiced_frames_frac', "degree_voice_breaks"
]